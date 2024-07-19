import os
import json


def run_pdflatex(filename):
    os.system(f"pdflatex -output-directory={os.getcwd()}/assets/pdflatex/ {filename}")
    return f"{os.getcwd()}/assets/pdflatex/"

def format_header_info (CV_data, entry_name):
    subtitle_info = CV_data["personal_details"]["subtitle_info"][entry_name]
    if "href" in subtitle_info.keys():
        href=f"\\color{{blue}} \\href{{{subtitle_info["href"]}}}"+"{"
        return subtitle_info["symbol"] + " \\enspace " + href + subtitle_info["value"]+"}"
    else:
        return subtitle_info["symbol"] + " \\enspace " + subtitle_info["value"]

def get_personal_info(CV_data, current_title):
    first_piece=f"""\\makecvtitle
\\vspace*{{-16mm}}
\\begin{{center}}
\\textbf{{{current_title}}}
\\end{{center}}

\\vspace*{{-4mm}}
% phone numbers 
\\begin{{center}}"""
    layout_subtitle = CV_data["personal_details"]["layout_subtitle"]
    
    rows_string=""
    for row in layout_subtitle["r"]:
        row_layout = layout_subtitle[row]
        row_text_before = "\\begin{tabular}{ " + "c"*len(row_layout) +"}\n"
        row_text="&  \\enspace".join([ 
            format_header_info(CV_data, entry)
            for entry in row_layout
            ])
        row_text_after = "\\end{tabular}\n"
        rows_string = rows_string + row_text_before + row_text + row_text_after

    return first_piece + rows_string + "\\end{center}\n"

def get_summary(summary_text):
    return f"\\section{{Profile}}\n{{{summary_text}}}\n"

def experience_bullet_point(
        experience_dict, 
        title, 
        employer_or_institution = None,
        bullet_points = "",
        show_dates=True
        ):
    
    if employer_or_institution == None:
        if "employer" in experience_dict.keys():
            employer_or_institution = experience_dict["employer"]
        elif "university" in experience_dict.keys():
            employer_or_institution = experience_dict["university"]
        else:
            raise Exception("No employer or univerisy")
    if isinstance(bullet_points, list):
        bullet_points="\\begin{itemize}[leftmargin=0.6cm, noitemsep, label={\\textbullet}]\n"+ "\n".join(
        [
            "\\item " + bullet for bullet in bullet_points
        ]) +"\n\\end{itemize}"
    if show_dates:
        dates = f"{experience_dict["start_date"]} - {experience_dict["end_date"]}"
    else:
        dates=""
    if "href" in experience_dict.keys():
        employer_or_institution_fill=f"\\color{{blue}}\\href{{{experience_dict["href"]}}}{{{employer_or_institution}}}"
    else:
        employer_or_institution_fill=f"\\color{{blue}}{employer_or_institution}"
    content = f"""\\customcventry{{{dates}}}{{{employer_or_institution_fill}}}{{{title}}}{{{experience_dict["city"]}}}{{}}{{{{{bullet_points}}}}}"""


    return content

def fill_work_experience(CV_data, job_titles, employer_names, bullet_points={}):
    experience =  CV_data["experience"]
    content = "\n\n".join([
        experience_bullet_point(experience[job], job_titles[job], employer_names[job], bullet_points[job]) if experience[job]["personalize"] else experience_bullet_point(experience[job], job_titles[job], employer_names[job], bullet_points = experience[job]["description_fixed"])
        for job in experience.keys()
    ])
    return f"\\section{{Work Experience}}\n" + content

def fill_education(CV_data, display_graduation_dates, titles={}, bullet_points={}):
    education =  CV_data["education"]
    if titles=={}:
        titles = {key: education[key]["title"] for key in education.keys()}
    content = "\n\n".join([
        experience_bullet_point(education[degree], titles[degree], bullet_points[degree], show_dates=display_graduation_dates) if education[degree]["personalize"] else experience_bullet_point(education[degree], titles[degree], bullet_points = education[degree]["description_fixed"], show_dates=display_graduation_dates)
        for degree in education.keys()
    ])
    return f"\\section{{Education}}\n" + content

def fill_awards(CV_data):
    awards =  CV_data["awards"]
    content= "{\\begin{itemize}[label=\\textbullet]\n" + "\n".join(
        [
            "\\item " + awards[award] 
            for award in awards.keys()
        ]
    ) + "\n\\end{itemize}}"
    return f"\\section{{Awards and achievements}}\n" + content

def fill_code_samples(CV_data):
    samples =  CV_data["code_samples"]
    content= "{\\begin{itemize}[label=\\textbullet]\n" + "\n".join(
        [
            "\\item " + samples[code] 
            for code in samples.keys()
        ]
    ) + "\n\\end{itemize}}"
    return f"\\section{{Code Samples}}\n" + content

def fill_skills(CV_data):
    skills =  CV_data["skills"]
    content= "{\\begin{itemize}[label=\\textbullet]\n" + "\n".join(
        [
            "\\item {" + f"\\textbf{{{skill}}}: " + ', '.join(skills[skill]) +"}"
            for skill in skills.keys()
        ]
    ) + "\n\\end{itemize}}"
    return f"\\section{{Skills}}\n" + content

def get_publications(CV_data):
    publications =  CV_data["publications"]
    content= "{\\begin{itemize}[label=\\textbullet]\n" + "\n".join(
        [
            "\\item " + publications[publication] 
            for publication in publications.keys()
        ]
    ) + "\n\\end{itemize}}"
    return f"\\section{{Publications}}\n" + content
    
def compile_CV(CV_data,
               job_title,
               company, 
               long_title,
               adapted_titles,
               adapted_employers,
               adapted_bullet_points,
               summary_text,  
               code_samples=True,
               display_graduation_dates=False,
               publications=False,
               scale=0.915
               ):
    cwd=os.getcwd()
    with open(cwd+'\\tex\\CV_blueprint\\imports.tex', 'r') as file:
        imports=file.read()

    imports=imports.replace("\\usepackage[scale=0.915]", f"\\usepackage[scale={scale}]")
    name = CV_data["personal_details"]["name"]
    surname = CV_data["personal_details"]["surname"]
    imports = imports + f"\n\n\\name{{{name}}}{{{surname}}}" + "\n\\begin{document}\n"
    header = get_personal_info(CV_data, long_title)

    summary = get_summary(summary_text)

    work = fill_work_experience(CV_data, adapted_titles, adapted_employers, adapted_bullet_points)
    
    education = fill_education(CV_data, display_graduation_dates)
    
    awards = fill_awards(CV_data)
    
    skills = fill_skills(CV_data)
    file = "\n".join(
            [
                imports,
                header,
                summary,
                work,
                education,
            ])
    
    if code_samples:
        file = file +"\n" +fill_code_samples(CV_data)

    file = file + "\n".join([awards, skills])

    if publications:
        file = file +"\n" +get_publications(CV_data)
        
    file = file + "\n\n\\end{document}"
    filename=f"{surname.upper()}.{company.replace(' ', '_')}.{job_title.replace(' ', '_')}"
    with open(cwd+f'\\tex\\{filename}.tex', 'w') as tex:
        tex.write(file)
    pdflatex_folder = run_pdflatex(cwd+f'\\tex\\{filename}.tex')
    return f"{pdflatex_folder}{filename}.pdf"
