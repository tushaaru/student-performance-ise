from flask import Flask, render_template, request, url_for
import random

app = Flask(__name__, static_folder="static", template_folder="templates")
db = {}

def student_key(student_id): return "student:" + student_id
def course_key(course_id): return "course:" + course_id
def assessment_key(course_id, assessment_id): return "assessment:" + course_id + ":" + assessment_id
def score_key(student_id, course_id, assessment_id): return "score:" + student_id + ":" + course_id + ":" + assessment_id
def performance_key(student_id, course_id): return "performance:" + student_id + ":" + course_id
def set_value(k,v): db[k]=v
def get_value(k): return db.get(k)
def keys_prefix(p): return [k for k in db if k.startswith(p)]
def add_student(student_id, name, branch, year, roll_no, attendance, sgpa, cgpa, backlogs, eligible, backlogSubjects=None):
    if backlogSubjects is None: backlogSubjects = []
    set_value(student_key(student_id), {"studentId": student_id, "name": name, "branch": branch, "year": year, "rollNo": roll_no, "attendance": attendance, "sgpa": sgpa, "cgpa": cgpa, "backlogs": backlogs, "eligible": eligible, "backlogSubjects": backlogSubjects})
def update_student_meta(student_id, **kwargs):
    s = get_value(student_key(student_id))
    if not s: return
    s.update(kwargs)
    set_value(student_key(student_id), s)
def add_course(course_id, name, hod):
    set_value(course_key(course_id), {"courseId": course_id, "name": name, "hod": hod})
def add_assessment(course_id, assessment_id, subject, title, max_marks):
    set_value(assessment_key(course_id, assessment_id), {"courseId": course_id, "assessmentId": assessment_id, "subject": subject, "title": title, "maxMarks": max_marks})
def add_score(student_id, course_id, assessment_id, marks_obtained):
    set_value(score_key(student_id, course_id, assessment_id), {"studentId": student_id, "courseId": course_id, "assessmentId": assessment_id, "marksObtained": marks_obtained})
def grade_from_percentage(p):
    if p>=90: return "A+"
    if p>=80: return "A"
    if p>=70: return "B+"
    if p>=60: return "B"
    if p>=50: return "C"
    if p>=40: return "D"
    return "F"
def compute_performance(student_id, course_id, subjects):
    totals = {s:{"obt":0,"max":0} for s in subjects}
    for k in keys_prefix(score_key(student_id, course_id, "")):
        sc = get_value(k)
        ass = get_value(assessment_key(course_id, sc["assessmentId"]))
        subj = ass["subject"]
        totals[subj]["obt"] += sc["marksObtained"]
        totals[subj]["max"] += ass["maxMarks"]
    total_obt = sum(v["obt"] for v in totals.values())
    total_max = sum(v["max"] for v in totals.values())
    pct = round((total_obt/total_max*100) if total_max else 0,2)
    grade = grade_from_percentage(pct)
    set_value(performance_key(student_id, course_id), {"studentId": student_id, "courseId": course_id, "totalMarks": total_obt, "maxTotalMarks": total_max, "percentage": pct, "grade": grade})
    return totals
def get_student_dashboard(student_id, course_id):
    s = get_value(student_key(student_id))
    p = get_value(performance_key(student_id, course_id))
    assessments_list = sorted(keys_prefix(assessment_key(course_id,"")))
    subjects_ordered = []
    subjects_set = []
    for ak in assessments_list:
        ass = get_value(ak)
        if ass and ass["subject"] not in subjects_set:
            subjects_set.append(ass["subject"])
            subjects_ordered.append(ass["subject"])
    subj_totals = []
    for sub in subjects_ordered:
        obtained = 0; maximum = 0
        for ak in assessments_list:
            ass = get_value(ak)
            if ass["subject"]==sub:
                sk = score_key(student_id, course_id, ass["assessmentId"])
                sc = get_value(sk)
                if sc:
                    obtained += sc["marksObtained"]
                maximum += ass["maxMarks"]
        subj_totals.append({"subject": sub, "obtained":obtained, "max":maximum})
    assessments=[]
    for ak in assessments_list:
        ass = get_value(ak)
        sk = score_key(student_id, course_id, ass["assessmentId"])
        sc = get_value(sk)
        assessments.append({"assessmentId": ass["assessmentId"], "title": ass["title"], "subject": ass["subject"], "maxMarks": ass["maxMarks"], "marksObtained": sc["marksObtained"] if sc else 0})
    return {"student": s, "performance": p, "subjects": subj_totals, "assessments": assessments}
def seed():
    random.seed(42)
    course_id = "ise_be"
    add_course(course_id, "B.E. Information Science & Engineering (ISE)", "Dr. Sumana Maradithaya")
    subjects = ["Data Structures", "Operating Systems", "Database Systems", "Computer Networks", "Artificial Intelligence"]
    assessment_counter = 1
    for subj in subjects:
        add_assessment(course_id, f"A{assessment_counter}", subj, f"{subj} - Quiz", 20); assessment_counter+=1
        add_assessment(course_id, f"A{assessment_counter}", subj, f"{subj} - Mid", 50); assessment_counter+=1
        add_assessment(course_id, f"A{assessment_counter}", subj, f"{subj} - End", 100); assessment_counter+=1
    first_names = ["Aadhya","Arjun","Bhavya","Chirag","Divya","Eshaan","Farhan","Gauri","Himansh","Ishita","Jatin","Kavya","Lakshmi","Manan","Nisha","Ojas","Pallavi","Rohit","Sneha","Tanya","Ujjwal","Vaishnavi","Xavier","Yash","Zara","Aditya","Bhoomi","Chetan","Darsh","Esha","Firoz","Gitanjali","Hiral","Irfan","Janhvi","Kiran","Lalit","Meera","Naveen","Oorja","Pranav","Rhea","Saurabh","Trisha","Uday","Vivek","Wahid","Yamini","Nikhil","Riya"]
    for i in range(50):
        roll = 201 + i
        sid = f"S{roll}"
        name = first_names[i % len(first_names)] + " " + ("Rao" if i%3==0 else "Kumar" if i%3==1 else "Sharma")
        attendance = round(random.uniform(62, 99),1)
        sgpa = round(random.uniform(5.0, 9.8), 2)
        cgpa = round(max(4.0, min(10.0, sgpa + random.uniform(-0.4,0.6))),2)
        add_student(sid, name, "ISE", "B.E", roll, attendance, sgpa, cgpa, 0, True, [])
    for k in keys_prefix(assessment_key(course_id,"")):
        ass = get_value(k)
        maxm = ass["maxMarks"]
        for skey in keys_prefix(student_key("")):
            base = int(maxm * 0.62)
            variance = int(maxm * 0.33)
            marks = max(0, min(maxm, random.randint(base-6, base+variance)))
            add_score(skey.split(":")[-1], course_id, ass["assessmentId"], marks)
    for skey in keys_prefix(student_key("")):
        sid = skey.split(":")[-1]
        compute_performance(sid, course_id, subjects)
    all_students = [s.split(":")[-1] for s in keys_prefix(student_key(""))]
    backlog_students = set(random.sample(all_students, 15))
    special_high = set(random.sample(list(backlog_students), 3))
    for sid in all_students:
        totals = compute_performance(sid, course_id, subjects)
        backlogSubjects = []
        for subj, vals in totals.items():
            maxm = vals["max"]
            obt = vals["obt"]
            pct = (obt / maxm * 100) if maxm else 0
            if pct < 40:
                backlogSubjects.append(subj)
        if sid in backlog_students and len(backlogSubjects) == 0:
            if sid in special_high:
                set_value(student_key(sid), {**get_value(student_key(sid)), "cgpa": round(random.uniform(8.0, 9.5),2)})
            victim = random.choice(subjects)
            victim_assessments = [get_value(ak) for ak in keys_prefix(assessment_key(course_id,"")) if get_value(ak)["subject"]==victim]
            if victim_assessments:
                chosen = random.choice(victim_assessments)
                sk = score_key(sid, course_id, chosen["assessmentId"])
                sc = get_value(sk)
                if sc:
                    new_marks = max(0, int(chosen["maxMarks"] * random.uniform(0.10, 0.28)))
                    set_value(sk, {"studentId": sid, "courseId": course_id, "assessmentId": chosen["assessmentId"], "marksObtained": new_marks})
            totals = compute_performance(sid, course_id, subjects)
            backlogSubjects = []
            for subj, vals in totals.items():
                maxm = vals["max"]
                obt = vals["obt"]
                pct = (obt / maxm * 100) if maxm else 0
                if pct < 40:
                    backlogSubjects.append(subj)
        if sid not in backlog_students and len(backlogSubjects) > 0:
            subj_to_fix = backlogSubjects[0]
            subject_assess = [get_value(ak) for ak in keys_prefix(assessment_key(course_id,"")) if get_value(ak)["subject"]==subj_to_fix]
            if subject_assess:
                chosen = random.choice(subject_assess)
                sk = score_key(sid, course_id, chosen["assessmentId"])
                sc = get_value(sk)
                if sc:
                    new_marks = min(chosen["maxMarks"], int(chosen["maxMarks"] * random.uniform(0.55, 0.8)))
                    set_value(sk, {"studentId": sid, "courseId": course_id, "assessmentId": chosen["assessmentId"], "marksObtained": new_marks})
            totals = compute_performance(sid, course_id, subjects)
            backlogSubjects = []
            for subj, vals in totals.items():
                maxm = vals["max"]
                obt = vals["obt"]
                pct = (obt / maxm * 100) if maxm else 0
                if pct < 40:
                    backlogSubjects.append(subj)
        s = get_value(student_key(sid))
        eligible = (s["cgpa"] >= 7.5) and (len(backlogSubjects) == 0)
        update_student_meta(sid, backlogs=len(backlogSubjects), backlogSubjects=backlogSubjects, eligible=eligible)
seed()
@app.route("/", methods=["GET","POST"])
def index():
    course = get_value(course_key("ise_be"))
    student_result = None
    error = None
    if request.method == "POST":
        roll = request.form.get("roll_no","").strip()
        if not roll:
            error = "Please enter a roll number."
        else:
            found = None
            for sk in keys_prefix(student_key("")):
                s = get_value(sk)
                if s and str(s["rollNo"])==str(roll):
                    found = s["studentId"]
                    break
            if not found:
                error = f"No student with roll number {roll}."
            else:
                student_result = get_student_dashboard(found, "ise_be")
    return render_template("index.html", course=course, student_result=student_result, error=error)
if __name__ == "__main__":
    app.run(debug=True)
