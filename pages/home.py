from dash import register_page, html, get_app, Input, Output, State, dcc, ALL
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from time import sleep
from dash_iconify import DashIconify
from utils.cv_compiler import compile_CV
import os
import json
from openai import OpenAI
from utils.prompts import prompt_summary, prompt_bulletpoints
from utils.constants import GPT_model

register_page(__name__, path='/')

labels_dropdowns={
    "employer": "Employer name",
    "job_titles": "Job Title",
    "start_date": "Start date",
    "end_date": "End date",
    "city": "City",
    "href": "link"
}

app=get_app()

with open(os.getcwd()+'\\tex\\CV_blueprint\\CV.json') as json_file:
    CV_data = json.load(json_file)
jobs_form_generator = {
    job: {
        "dropdowns": [key for key in CV_data['experience'][job].keys() if isinstance(CV_data['experience'][job][key], list)], 
        "bullet_points": CV_data['experience'][job]["personalize"]
        }
    for job in CV_data['experience'].keys()
}

def bullet_boxes(job, generate):
    if generate:
        return [html.H5('ChatGPT-generated bulletpoints'), dcc.Markdown(id=f"bullets-textbox-{job}-answer", children='<ChatGPT response here>')]+[dmc.Stack(sum(
            [
                [
                    dmc.TextInput(
                        id={"type": f"bullets-textbox-{job}", "index": f'{i}'}, 
                        label=f"Bullet point {i+1}",
                        w=800, 
                        ),
                    dmc.Checkbox(
                        id={"type": f"bullets-checkbox-{job}", "index": f'{i}'}, 
                        label=f"Include bullet point {i+1}", 
                        checked=True, 
                        ),
                ] 
                for i in range(5)
            ], []))]
    else:
        return []
    
def layout():
    
    auto_fill_form=[
        html.H2('AI Auto-Fill'),
        dmc.Stack(
            [
                dmc.TextInput(label="Company Name", w=300, id="company-name"),
                dmc.TextInput(label="Position Name", w=300, id="position-name"),
            ]
        ),        
        dmc.Textarea(
            id="job_ad",
            label="Job Ad",
            placeholder="Paste the job ad here",
            w=1000,
            autosize=True,
            minRows=2,
        ),
        dmc.Center(
                [
                    dmc.Button("Auto-Fill", id='fill_start',  w=120),
                ],
            ),
        ]
    
    header_form=[
        html.H3('Header'),
        dmc.Stack(
            [
                dmc.Select(
                    label="Enthusiastic about",
                    placeholder="Select one",
                    id="title-select-topic",
                    value=CV_data["personal_details"]["enthusiastic_about"][0]["value"],
                    data=CV_data["personal_details"]["enthusiastic_about"],
                    w=200,
                    mb=10,
                ),
                dmc.Select(
                    label="Last job title",
                    placeholder="Select one",
                    id="title-select-job",
                    value=CV_data['experience'][list(CV_data['experience'].keys())[0]]["job_titles"][0],
                    data=CV_data['experience'][list(CV_data['experience'].keys())[0]]["job_titles"],
                    w=200,
                    mb=10,
                ),
                dmc.TextInput(label="Subtitle", w=600, id="subtitle", value=CV_data["personal_details"]["default_long_title"]),
            ]
        ),
    ]
    summary_form = [
        html.H3('Summary'),
        dmc.Textarea(
            id='summary',
            label="Summary",
            placeholder="Summary",
            w=1000,
            autosize=True,
            minRows=2,
        ),]
    job_elements=sum(
        [
            [html.H4(job)] + [
                dmc.Select(
                    label=labels_dropdowns[key],
                    placeholder="Select one",
                    id={"type": f"experience-select-{key}", "index": j},
                    value=CV_data['experience'][job][key][0],
                    data=CV_data['experience'][job][key],
                    w=200,
                    mb=10,
                ) for key in jobs_form_generator[job]["dropdowns"]
            ] +  bullet_boxes(job, jobs_form_generator[job]["bullet_points"]) + [
                dcc.Store(id={"type": "job-stores-bullets", "index": j})
            ] 
        for j, job in enumerate(jobs_form_generator.keys())
        ], [])

    jobs_form = [
        html.H3('Jobs'),
        dcc.Store(id="jobs-store"),
        dcc.Store(id="job-store-job_titles"),
        dcc.Store(id="job-store-employer")
    ]+job_elements
    education_form= [
        html.H3('Education'),
        dmc.Select(
            label="Show dates",
            placeholder="Select one",
            id="show-dates",
            value="Almost Graduated",
            data=[
                "Yes",
                "Almost Graduated", #will be purged soon
                "No"
            ],
            w=200,
            mb=10,
        )]
    experience_form=header_form + summary_form + jobs_form + education_form
    final_form_and_compile=[
            html.H3('Code Samples'),
            dmc.Select(
                label="Include Code Samples",
                placeholder="Select one",
                id="include-code-samples",
                value="Yes",
                data=[
                    "Yes",
                    "No"
                ],
                w=200,
                mb=10,
            ),
            html.H3('Courses'),
            dmc.Select(
                label="Include Courses",
                placeholder="Select one",
                id="include-courses",
                value="Yes",
                data=[
                    "Yes",
                    "No"
                ],
                w=200,
                mb=10,
            ),
            html.H3('Publications'),
            dmc.Select(
                label="Include Publications",
                placeholder="Select one",
                id="include-publications",
                value="Yes",
                data=[
                    "Yes",
                    "No"
                ],
                w=200,
                mb=10,
            ),
            html.H3('Scale'),
            dmc.Slider(
                id="scale_slider",
                min=0.8, max=1, step=0.001, value=0.915
            ),
            dmc.Center(
                [
                    dmc.Button("Compile CV", id='compile_start',  w=120),
                    dcc.Download(id="download-pdf"),
                ],
            ),
            html.Div(id='notification'),
            html.Div(id='notification-2'),
        ]
    layout = html.Div(
        children = auto_fill_form + [html.H2('Manual Edit')] + experience_form + final_form_and_compile,
        className='main_inputs',
    )
    return layout

@app.callback(
    Output("subtitle", "value"),
    Input("title-select-job", "value"), 
    Input("title-select-topic", "value"),
    prevent_initial_call=True
)
def update_title(title, topic):
    fstring = CV_data["personal_details"]["title_fstring"]
    fstring = fstring.format(title=title, topic=topic)
    return fstring




# store for each job the bullets in its store
for j, job in enumerate(jobs_form_generator.keys()): 
    if jobs_form_generator[job]["bullet_points"]: 
        @app.callback(
            Output({"type": "job-stores-bullets", "index": j}, 'data'),
            Input({'type': f'bullets-checkbox-{job}', 'index': ALL}, 'checked'),
            Input({'type': f'bullets-textbox-{job}', 'index': ALL}, 'value'),
        )
        def update_job_bullets_store(checkboxes, value):
            list_of_points=[value[i] for i, checkbox in enumerate(checkboxes) if checkbox]
            return list_of_points

# copy all stores in a central one
@app.callback(
    Output("jobs-store", 'data'),
    inputs=sum([
        [Input({"type": "job-stores-bullets", "index": ALL}, 'modified_timestamp'),
        State({"type": "job-stores-bullets", "index": ALL}, 'data')]
        for job in jobs_form_generator.keys() if jobs_form_generator[job]["bullet_points"]
        ], [])
)
def update_all_jobs_bullets_store(timestamps, stores):
    jobs=[job for job in jobs_form_generator.keys() if jobs_form_generator[job]["bullet_points"]]
    return {
        job: stores[i] for i, job in enumerate(jobs)
    }


@app.callback(
    Output("job-store-job_titles", 'data'),
    Input({"type": "experience-select-job_titles", "index": ALL}, 'value'),
)
def update_job_bullets_store(values):
    jobs=[job for job in jobs_form_generator.keys() if "job_titles" in jobs_form_generator[job]["dropdowns"]]
    return {
        job: values[i] for i, job in enumerate(jobs)
    }

@app.callback(
    Output("job-store-employer", 'data'),
    Input({"type": "experience-select-employer", "index": ALL}, 'value'),
)
def update_job_bullets_store(values):
    jobs=[job for job in jobs_form_generator.keys() if "employer" in jobs_form_generator[job]["dropdowns"]]
    return {
        job: values[i] for i, job in enumerate(jobs)
    }


@app.callback(
    output=[
        Output("notification-2", "children"),
        Output("summary", "value"),
    ]+[
        #Output({'type': f'bullets-textbox-{job}', 'index': ALL}, 'value') for job in jobs_form_generator.keys() if jobs_form_generator[job]["bullet_points"]
        Output(f'bullets-textbox-{job}-answer', 'children') for job in jobs_form_generator.keys() if jobs_form_generator[job]["bullet_points"]
    ],
    inputs=[
        Input("fill_start", "n_clicks"),
        State("position-name", "value"),
        State("company-name", "value"),
        State("job_ad", "value"),
    ],
    running=[
        (Output("fill_start", "loading"), True, False),
    ],
    prevent_initial_call=True,
)
def fill_funciton(n_clicks, job_title, company, job_ad):
    with open(os.getcwd()+'\\tex\\CV_blueprint\\CV.txt') as file:
        CV_text=file.read()
    client = OpenAI()
    summary = client.chat.completions.create(
        model=GPT_model,
        messages=[
            {"role": "system", "content": prompt_summary.format(job_title=job_title, company=company)},
            {"role": "user", "content": f"Here is a summary of the contents of my CV, the job ad will be in the next message: {CV_text}"},
            {"role": "assistant", "content": "Ok! I will reply with a couple of lines to put on your CV as a profile summary, appropriate for the position you are applying to, when you send me a the position you are applying to"},
            {"role": "user", "content": job_ad}
        ]
    )
    summary=summary.choices[0].message.content 
    # need to generalize in the future
    with open(os.getcwd()+'\\tex\\CV_blueprint\\ecb.txt') as file:
        ecb=file.read()
    bullets = client.chat.completions.create(
        model=GPT_model,
        messages=[
            {"role": "system", "content": prompt_bulletpoints.format(job_title=job_title, company=company)},
            {"role": "user", "content": f"Here is a summary of what I did at the ECB, the job ad will be in the next message: {ecb}"},
            {"role": "assistant", "content": "Ok! I will reply with a 5 bulletpoints to put on your CV related to your work at ECB, appropriate for the position you are applying to, when you send me a the position you are applying to"},
            {"role": "user", "content": job_ad}
        ]
    )
    bullets=bullets.choices[0].message.content
    notification = dmc.Notification(
        title="Success!",
        id="compiled-notify",
        action="show",
        message="Chat-GPT replied successfully!",
        icon=DashIconify(icon="ic:round-celebration"),
    )
    return (notification, summary, bullets)
    


@app.callback(
    output=[
        Output("notification", "children"),
        Output("download-pdf", "data"),
    ],
    inputs=[
        Input("compile_start", "n_clicks"),
        State("position-name", "value"),
        State("company-name", "value"),
        State("subtitle", "value"),
        State("summary", "value"),
        State("job-store-job_titles", 'data'),
        State("job-store-employer", 'data'),
        State("jobs-store", 'data'),
        State("show-dates", 'value'),
        State("include-code-samples", 'value'),
        State("include-courses", 'value'),
        State("include-publications", 'value'),
        State("scale_slider", 'value'),
    ],
    running=[
        (Output("compile_start", "loading"), True, False),
    ],
    prevent_initial_call=True,
)
def compile_funciton(n_clicks, 
                     job_title, 
                     company, 
                     long_title, 
                     summary, 
                     adapted_titles, 
                     adapted_employers,
                     adapted_bullet_points,
                     display_graduation_dates,
                     code_samples,
                     courses,
                     publications,
                     scale
                     ):
    if display_graduation_dates == "Yes":
        display_graduation_dates = True
    elif display_graduation_dates == "No":
        display_graduation_dates = False
    else:
        display_graduation_dates = 'almost-graduated'
    # display_graduation_dates = display_graduation_dates == "Yes"
    code_samples = code_samples == "Yes"
    publications = publications == "Yes"
    path = compile_CV(
            CV_data=CV_data,
            job_title=job_title,
            company=company, 
            long_title=long_title, 
            adapted_titles = adapted_titles,
            adapted_employers = adapted_employers,
            adapted_bullet_points= adapted_bullet_points,
            summary_text=summary, 
            code_samples=code_samples,
            courses=courses,
            display_graduation_dates=display_graduation_dates,
            publications=publications,
            scale=scale)
    return (dmc.Notification(
        title="Success!",
        id="compiled-notify",
        action="show",
        message="Your CV was compiled!",
        icon=DashIconify(icon="ic:round-celebration"),
    ),
    dcc.send_file(path),
    )