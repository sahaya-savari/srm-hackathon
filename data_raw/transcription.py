"""
RAW LAYER — human-verified visual transcription of the 10 timetable PDFs.

All 10 PDFs are image-only scans (0 bytes of extractable text), so every
value below was read from the rendered page image and cross-checked against
a Tesseract pass (see pipeline/ocr_crosscheck.py). Nothing here is inferred:
empty cells are empty, handwritten edits are marked, and cell text is kept
verbatim (normalisation happens in pipeline/normalize.py, not here).

Grid cell format: (day, first_period, last_period, raw_text, note)
  - merged cells span first_period..last_period
  - note: '' | 'handwritten' | 'faded' | 'typo'
"""

GRID_2026 = {  # period -> (start, end) for all 2026-27 timetables (9 files)
    1: ("09:00", "09:50"), 2: ("09:50", "10:40"),  # tea break 10:40-10:50
    3: ("10:50", "11:40"), 4: ("11:40", "12:30"),
    5: ("12:30", "13:20"),                         # LUNCH in every 2026-27 grid
    6: ("13:20", "14:10"), 7: ("14:10", "15:00"),  # tea break 15:00-15:10
    8: ("15:10", "16:00"), 9: ("16:00", "16:50"),
}
GRID_2024_I_YEAR = {  # different bell schedule used by the I-year file
    1: ("09:00", "09:50"), 2: ("09:55", "10:45"), 3: ("10:50", "11:40"),
    4: ("11:45", "12:35"), 5: ("12:35", "13:30"), 6: ("13:30", "14:20"),
    7: ("14:25", "15:15"), 8: ("15:20", "16:10"), 9: ("16:15", "17:05"),
}

# subject rows: slot -> (code, name, LTPC, faculty, designation)
SECTIONS = {
 # ------------------------------------------------------------------ IV ECE A
 "IV-ECE-A": dict(
  source_file="IV ECE A.pdf", page=1, academic_year="2026-27", semester_type="Odd",
  year=4, semester=7, dept="ECE", venue="IST 225", grid="GRID_2026",
  approval_date="17/07/2026",
  subjects={
   "A": ("21GNH401T", "Behavioural Psychology", "2-1-0-3", "Dr.A.Anand", "AP/ECE"),
   "B": ("21ECC401T", "Wireless Communication and Antenna Systems", "3-0-0-3", "Dr.K.Vigneshwaran", "AP/ECE"),
   "C": ("21ECC402P", "Computer Communication and Network Security", "2-1-0-3", "Dr.S.Jeevanantham", "AP/ECE-DS"),
   "D": ("21ECE461T", "Semiconductor Memory Design", "3-0-0-3", "Dr. H.SriBhuvaneshwari", "AP/ECE"),
   "E": ("21ECE463T", "Scripting Language for Electronic Design Automation", "3-0-0-3", "Dr. Sreenivasa Rao Ijada", "Prof/ECE"),
   "F": ("21CSO355T", "Machine learning for all", "3-0-0-3", "Dr.N.Prasanna Venkatesh", "AP/BME"),
   "LAB": ("21ECC402P", "Computer Communication and Network Security", "2-1-0-3", "Mrs.T.Swetha", "AP/ECE"),
  },
  cells=[
   ("Mon",1,1,"C",""),("Mon",3,3,"A",""),("Mon",4,4,"D",""),
   ("Tue",1,1,"C",""),("Tue",2,2,"D",""),("Tue",3,3,"B",""),("Tue",4,4,"F",""),
   ("Wed",1,1,"B",""),("Wed",2,2,"LAB - IST 108",""),("Wed",3,3,"E",""),("Wed",4,4,"F",""),
   ("Thu",1,1,"F",""),("Thu",2,2,"A",""),("Thu",3,3,"E",""),("Thu",4,4,"B",""),
   ("Fri",1,1,"C",""),("Fri",2,2,"A",""),("Fri",3,3,"D",""),("Fri",4,4,"E",""),
  ]),
 # ------------------------------------------------------------------ IV ECE B
 "IV-ECE-B": dict(
  source_file="IV ECE B.pdf", page=1, academic_year="2026-27", semester_type="Odd",
  year=4, semester=7, dept="ECE", venue="IST 227", grid="GRID_2026",
  approval_date="17/07/2026",
  subjects={
   "A": ("21GNH401T", "Behavioural Psychology", "2-1-0-3", "Dr.A.Annand", "AP/ECE"),
   "B": ("21ECC401T", "Wireless Communication and Antenna Systems", "3-0-0-3", "Dr.K.Vigneshwaran", "AP/ECE"),
   "C": ("21ECC402P", "Computer Communication and Network Security", "2-1-0-3", "Dr. R. Rajasekar", "ASP & HOD ECE-DS"),
   "D": ("21ECE461T", "Semiconductor Memory Design", "3-0-0-3", "Dr. H.SriBhuvaneshwari", "AP/ECE"),
   "E": ("21ECE463T", "Scripting Language for Electronic Design Automation", "3-0-0-3", "Dr. Sreenivasa Rao Ijada", "Prof/ECE"),
   "F": ("21CSO355T", "Machine learning for all", "3-0-0-3", "Dr.N.Prasanna Venkatesh", "AP/BME"),
   "LAB": ("21ECC402P", "Computer Communication and Network Security", "2-1-0-3", "Ms.T.Swetha", "AP/ECE"),
  },
  cells=[
   ("Mon",1,1,"C",""),("Mon",2,2,"A",""),("Mon",3,3,"E",""),("Mon",4,4,"F",""),
   ("Tue",1,1,"C",""),("Tue",2,2,"E",""),("Tue",3,3,"F",""),("Tue",4,4,"B",""),
   ("Wed",1,1,"C",""),("Wed",2,2,"D",""),("Wed",3,3,"A",""),("Wed",4,4,"B",""),
   ("Thu",1,1,"D",""),("Thu",2,2,"B",""),("Thu",3,3,"LAB - IST 108",""),("Thu",4,4,"A",""),
   ("Fri",1,1,"E",""),("Fri",2,2,"D",""),("Fri",3,3,"F",""),
  ]),
 # ------------------------------------------------------------------ III ECE A
 "III-ECE-A": dict(
  source_file="III ECE A.pdf", page=1, academic_year="2026-27", semester_type="Odd",
  year=3, semester=5, dept="ECE", venue="IST 518/FN", grid="GRID_2026",
  approval_date="17/07/2026",
  subjects={
   "A": ("21MAB302T", "Discrete Mathematics", "3-1-0-4", "New Faculty 3", "AP/Maths"),
   "B": ("21ECC301P", "Microprocessor, Microcontroller, and Interfacing Techniques", "3-1-0-4", "Dr.M.Manikandan", "AP/ECE"),
   "C": ("21ECC303T", "VLSI Design and Technology", "3-0-0-3", "Dr.M.Jothi", "AP/ECE"),
   "D": ("21ECE468T", "System and Network on Chip", "3-0-0-3", "Dr.V. Manikandan", "AP/ECE-DS"),
   "E": ("21CSO355T", "Machine learning for all", "3-0-0-3", "Dr. J.Jencia", "AP/BME"),
   "F": ("21GNP301L", "Community connect", "0-0-2-1", "Dr.V .Rajesh / Dr. V.Bharathi", "AP/ECE"),
   "G": ("21PDM301L", "Analytical and logical thinking skills", "0-0-2-0", "CDC / 625", ""),
   "H": ("21LEM301T", "Indian Art Form", "1-0-0-0", "Dr.K.Vigneshwaran", "AP/ECE"),
   "LAB": ("21ECC311L", "VLSI Design/ Microprocessor Laboratory", "0-0-4-2", "Dr.M.Jothi & Dr. P. Murugapandiyan / Dr.V. Manikandan", "AP/ECE; Prof./ECE; AP/ECE-DS"),
  },
  cells=[
   ("Mon",1,1,"E",""),("Mon",2,2,"B",""),("Mon",3,3,"B",""),("Mon",4,4,"A",""),("Mon",6,7,"G – 625",""),
   ("Tue",1,1,"H",""),("Tue",2,2,"D",""),("Tue",3,3,"B",""),("Tue",4,4,"B-Proj",""),("Tue",7,7,"G - 625",""),
   ("Wed",1,1,"C",""),("Wed",2,2,"A",""),("Wed",3,3,"D",""),("Wed",4,4,"F",""),("Wed",8,9,"LAB-108/309",""),
   ("Thu",1,1,"A",""),("Thu",2,2,"E",""),("Thu",3,3,"C",""),("Thu",4,4,"F",""),
   ("Fri",1,1,"D",""),("Fri",2,2,"A",""),("Fri",3,3,"E",""),("Fri",4,4,"C",""),("Fri",6,7,"LAB-108/309",""),
  ]),
 # ------------------------------------------------------------------ III ECE B
 "III-ECE-B": dict(
  source_file="III ECE B.pdf", page=1, academic_year="2026-27", semester_type="Odd",
  year=3, semester=5, dept="ECE", venue="IST 518/AN", grid="GRID_2026",
  approval_date="17/07/2026",
  subjects={
   "A": ("21MAB302T", "Discrete Mathematics", "3-1-0-4", "Dr.M.Thanga Rejini", "AP/Maths"),
   "B": ("21ECC301P", "Microprocessor, Microcontroller, and Interfacing Techniques", "3-1-0-4", "Mrs. B. Abirami", "EO/SRMIST"),
   "C": ("21ECC303T", "VLSI Design and Technology", "3-0-0-3", "Dr.R.Vinoth Raj", "AP/ECE-DS"),
   "D": ("21ECE468T", "System and Network on Chip", "3-0-0-3", "Dr.V. Manikandan", "AP/ECE-DS"),
   "E": ("21CSO355T", "Machine learning for all", "3-0-0-3", "Dr. J.Jencia", "AP/BME"),
   "F": ("21GNP301L", "Community connect", "0-0-2-1", "Dr. H. Sudharsan / Ms. T.Swetha", "AP/ECE"),
   "G": ("21PDM301L", "Analytical and logical thinking skills", "0-0-2-0", "CDC – 625", ""),
   "H": ("21LEM301T", "Indian Art Form", "1-0-0-0", "Dr. A.Anand", "AP/ECE"),
   "LAB": ("21ECC311L", "VLSI Design/ Microprocessor Laboratory", "0-0-4-2", "Dr.Sreenivasa Ijada Rao / Dr. B. DeviSri & Dr. Prassanna Venkatesh", "Prof./ECE; AP/ECE; AP/BME"),
  },
  cells=[
   ("Mon",1,2,"LAB-108/309",""),("Mon",6,6,"E",""),("Mon",7,7,"B",""),("Mon",8,8,"A",""),("Mon",9,9,"D",""),
   ("Tue",1,2,"G-625",""),("Tue",6,6,"F",""),("Tue",7,7,"B",""),("Tue",8,8,"D",""),("Tue",9,9,"C",""),
   ("Wed",1,1,"G - 625",""),("Wed",6,6,"B-Proj",""),("Wed",7,7,"B",""),("Wed",8,8,"A",""),("Wed",9,9,"H",""),
   ("Thu",1,2,"LAB-108/309",""),("Thu",6,6,"A",""),("Thu",7,7,"C",""),("Thu",8,8,"E",""),("Thu",9,9,"F",""),
   ("Fri",6,6,"C",""),("Fri",7,7,"A",""),("Fri",8,8,"E",""),("Fri",9,9,"D",""),
  ]),
 # ------------------------------------------------------------------ III ECE DS
 "III-ECE-DS": dict(
  source_file="III ECE DS.pdf", page=1, academic_year="2026-27", semester_type="Odd",
  year=3, semester=5, dept="ECE-DS", venue="IST 519/FN", grid="GRID_2026",
  approval_date=None,
  subjects={
   "A": ("21MAB302T", "Discrete Mathematics", "3-1-0-4", "New faculty 2", "AP/Maths"),
   "B": ("21ECC301P", "Microprocessor, Microcontroller, and Interfacing Techniques", "3-1-0-4", "Mrs. B. Abirami", "EO/SRMIST"),
   "C": ("21ECC303T", "VLSI Design and Technology", "3-0-0-3", "Dr.R.Vinoth Raj", "AP/ECE-DS"),
   "D": ("21CSO355T", "Machine learning for all", "3-0-0-3", "Dr. Dr.Chitra Devi", "ASP/SoC"),
   "E": ("21ECE371T", "Database Design and Management", "3-0-0-3", "Dr. S.Saraswathi", "AP/SoC"),
   "F": ("21GNP301L", "Community connect", "0-0-2-1", "Dr. S.Jeevanantham / Dr.V. Manikandan", "AP/ECE-DS"),
   "G": ("21PDM301L", "Analytical and logical thinking skills", "0-0-2-0", "CDC-625", ""),
   "H": ("21LEM301T", "Indian Art Form", "1-0-0-0", "Dr.Prabin Kumar Bera", "AP/ECE"),
   "LAB": ("21ECC311L", "VLSI Design/ Microprocessor Laboratory", "0-0-4-2", "Dr. R. Vinothraj / Dr. H. Sri Bhuvaneshwari", "AP/ECE DS; AP/ECE"),
  },
  cells=[
   ("Mon",1,1,"E",""),("Mon",2,2,"B",""),("Mon",3,3,"C",""),("Mon",4,4,"A",""),
   ("Tue",1,1,"C",""),("Tue",2,2,"B",""),("Tue",3,3,"D",""),("Tue",4,4,"F",""),("Tue",6,7,"LAB-108/107",""),
   ("Wed",1,1,"H",""),("Wed",2,2,"B",""),("Wed",3,3,"A",""),("Wed",4,4,"C",""),("Wed",8,9,"G-625",""),
   ("Thu",1,1,"A",""),("Thu",2,2,"D",""),("Thu",3,3,"E",""),("Thu",4,4,"F",""),
   ("Fri",1,1,"D",""),("Fri",2,2,"A",""),("Fri",3,3,"E",""),("Fri",4,4,"B-Proj",""),("Fri",6,6,"G-625",""),("Fri",8,9,"LAB-108/107",""),
  ]),
 # ------------------------------------------------------------------ III BME
 "III-BME": dict(
  source_file="III BME.pdf", page=1, academic_year="2026-27", semester_type="Odd",
  year=3, semester=5, dept="BME", venue="IST 211 / AN", grid="GRID_2026",
  approval_date=None,
  subjects={
   "A": ("21MAB301T", "Probability and Statistics", "3-1-0-4", "Dr. K. M. Karuppusamy", "AP/Maths"),
   "B": ("21BMC302J", "Microcontrollers and Its Application in Medicine", "3-0-2-4", "Dr.K.Vigneshwaran", "ASP/ECE"),
   "C": ("21BMC301J", "Biomedical Signal Processing", "3-0-2-4", "Dr. V.N. Senthilkumaran", "ASP & HOD / ECE"),
   "D": ("21BME266T", "Biometrics", "3-0-0-3", "Dr. G. Gifta", "AP/BME"),
   "E": ("21ECO103T", "Modern wireless communication system", "3-0-0-3", "Dr. Vaishnavi", "AP/ECE"),
   "F": ("21BMC303T", "Principles of Medical Imaging", "3-0-0-3", "Dr.N.Prasana venkatesh", "AP/BME"),
   "G": ("21PDM301L", "Analytical and Logical Thinking Skills", "0-0-2-0", "CDC-625", ""),
   "H": ("21LEM301T", "Indian Art Form", "1-0-0-0", "Dr. G. Gifta", "AP/BME"),
   "I": ("21GNP301L", "Community Connect", "0-0-2-1", "Dr. J.Jencia / Dr.N.Prasanna Venkatesh", "AP/BME"),
  },
  cells=[
   ("Mon",1,2,"G-625",""),("Mon",3,4,"MPMC LAB-107",""),("Mon",6,6,"E",""),("Mon",7,7,"B",""),("Mon",8,8,"F",""),("Mon",9,9,"H",""),
   ("Tue",1,2,"BIO DSP LAB-108",""),("Tue",3,3,"G-625",""),("Tue",6,6,"C",""),("Tue",7,7,"D",""),("Tue",8,8,"A",""),("Tue",9,9,"B",""),
   ("Wed",6,6,"C",""),("Wed",7,7,"A",""),("Wed",8,8,"F",""),("Wed",9,9,"D",""),
   ("Thu",4,4,"I-108",""),("Thu",6,6,"A",""),("Thu",7,7,"C",""),("Thu",8,8,"E",""),("Thu",9,9,"B",""),
   ("Fri",1,1,"I-108",""),("Fri",6,6,"F",""),("Fri",7,7,"A",""),("Fri",8,8,"D",""),("Fri",9,9,"E",""),
  ]),
 # ------------------------------------------------------------------ II BME
 "II-BME": dict(
  source_file="II BME.pdf", page=1, academic_year="2026-27", semester_type="Odd",
  year=2, semester=3, dept="BME", venue="IST 602 / FN", grid="GRID_2026",
  approval_date=None,
  subjects={
   "A": ("21MAB201T", "Transforms and Boundary Value Problems", "3-1-0-4", "Dr.A.Manickam", "ASP/MAT"),
   "B": ("21BMC202T", "Biomedical Signals and Systems", "3-0-0-3", "Dr. Senthil Kumaran V N", "ASP & HOD / ECE"),
   "C": ("21BMC203J", "Electric and Electronic Circuits", "3-0-2-4", "Dr. Prabin Kumar Bera", "AP/ECE"),
   "D": ("21BMC204J", "Digital Logic for Medical Systems", "2-0-2-3", "Dr. G. Gifta", "AP/BME"),
   "E": ("21PYS202T", "Medical Physics", "3-0-0-3", "Dr.D.Rajeswari", "ASP/PHY"),
   "F": ("21LEM201T", "Professional Ethics", "1-0-0-0", "Dr. H.SriBhuvaneshwari", "AP/ECE"),
   "G": ("21LEM202T", "Universal Human Values-II", "2-1-0-3", "Mrs.N.Suganthi", "RS - ECE"),
   "H": ("21PDM201L", "Verbal Reasoning", "0-0-2-0", "CDC-TB-106", ""),
   "I": ("21PDH201T", "Social Engineering", "2-0-0-2", "Mrs. Francis Arockiya Mary", "RS - EEE"),
  },
  cells=[
   ("Mon",1,1,"E",""),("Mon",2,2,"C",""),("Mon",3,4,"I",""),("Mon",6,7,"DLMS/EEC-107,309",""),
   ("Tue",1,1,"C",""),("Tue",2,2,"E",""),("Tue",3,3,"B",""),("Tue",4,4,"A",""),("Tue",6,7,"H-TB-106",""),
   ("Wed",1,1,"B",""),("Wed",2,2,"D",""),("Wed",3,3,"A",""),("Wed",6,6,"H-TB-106",""),("Wed",7,7,"G-602",""),
   ("Thu",1,1,"A",""),("Thu",2,2,"E",""),("Thu",3,3,"B",""),("Thu",4,4,"D",""),("Thu",8,9,"DLMS/EEC-107,309",""),
   ("Fri",1,1,"F",""),("Fri",2,2,"A",""),("Fri",3,3,"C",""),("Fri",4,4,"D",""),("Fri",8,9,"G-602",""),
  ]),
 # ------------------------------------------------------------------ II ECE DS A
 "II-ECE-DS-A": dict(
  source_file="II ECE DS A.pdf", page=1, academic_year="2026-27", semester_type="Odd",
  year=2, semester=3, dept="ECE-DS", venue="IST 416 / FN", grid="GRID_2026",
  approval_date=None,
  subjects={
   "A": ("21MAB201T", "Transforms and Boundary Value Problems", "3-1-0-4", "Dr.C. Arun Kumar", "AP/Maths"),
   "B": ("21ECC201T", "Solid State Devices", "3-0-0-3", "Dr. Jeevanantham S", "AP/ECE-DS"),
   "C": ("21CSS201T", "Computer Organization and Architecture", "3-1-0-4", "Dr. P. Murugapandiyan", "Prof./ECE"),
   "D": ("21ECC203T", "Digital Logic Design", "3-0-0-3", "Dr.S.Krishnakumar", "AP/ECE-DS"),
   "E": ("21ECC205T", "Electromagnetic Theory and Interference", "3-0-0-3", "Dr.V. Bharathi", "AP/ECE"),
   "F": ("21LEM201T", "Professional Ethics", "1-0-0-0", "Dr. Jothi M", "AP/ECE"),
   "G": ("21LEM202T", "Universal Human Values-II", "2-1-0-3", "Mrs.N.Suganthi", "RS - ECE"),
   "H": ("21PDM201L", "Verbal Reasoning", "0-0-2-0", "CDC – TB -106", ""),
   "I": ("21PDH209T", "Social Engineering", "2-0-0-2", "Mrs.D. Lavanya", "RS - ECE"),
   "LAB": ("21ECC211L", "Devices and Digital IC Laboratory", "0-0-4-2", "Dr. Jeevanantham S / Dr.V. Bharathi", "AP/ECE-DS; AP/ECE"),
  },
  cells=[
   ("Mon",1,1,"E",""),("Mon",2,2,"A",""),("Mon",3,4,"I",""),("Mon",6,7,"G-602",""),("Mon",8,9,"LAB -309/107",""),
   ("Tue",1,1,"C",""),("Tue",2,2,"A",""),("Tue",3,3,"E",""),("Tue",4,4,"D",""),("Tue",6,6,"G-602",""),("Tue",8,9,"H-TB -106",""),
   ("Wed",1,1,"A",""),("Wed",2,2,"B",""),("Wed",3,3,"C",""),("Wed",4,4,"D",""),("Wed",7,7,"H-TB - 106",""),
   ("Thu",1,1,"B",""),("Thu",2,2,"C",""),("Thu",3,3,"A",""),("Thu",4,4,"F",""),("Thu",6,7,"LAB -309/107",""),
   ("Fri",1,1,"D",""),("Fri",2,2,"B",""),("Fri",3,3,"E",""),("Fri",4,4,"C",""),
  ]),
 # ------------------------------------------------------------------ II ECE DS B
 "II-ECE-DS-B": dict(
  source_file="II ECE DS B.pdf", page=1, academic_year="2026-27", semester_type="Odd",
  year=2, semester=3, dept="ECE-DS", venue="IST 411/ AN", grid="GRID_2026",
  approval_date=None,
  subjects={
   "A": ("21MAB201T", "Transforms and Boundary Value Problems", "3-1-0-4", "NEW FACULTY 3", "AP/MAT"),
   "B": ("21ECC201T", "Solid State Devices", "3-0-0-3", "Dr. Jeevanantham S", "AP/ECE DS"),
   "C": ("21CSS201T", "Computer Organization and Architecture", "3-1-0-4", "Dr. P. Murugapandiyan", "Prof./ECE"),
   "D": ("21ECC203T", "Digital Logic Design", "3-0-0-3", "Dr.S.Krishnakumar", "AP/ECE DS"),
   "E": ("21ECC205T", "Electromagnetic Theory and Interference", "3-0-0-3", "Dr.V. Bharathi", "AP/ECE"),
   "F": ("21LEM201T", "Professional Ethics", "1-0-0-0", "Dr. K. Vigneshwaran", "AP/ECE"),
   "G": ("21LEM202T", "Universal Human Values-II", "2-1-0-3", "Mrs.D.Lavanya", "RS - ECE"),
   "H": ("21PDM201L", "Verbal Reasoning", "0-0-2-0", "CDC-TB-106", ""),
   "I": ("21PDH209T", "Social Engineering", "2-0-0-2", "Mrs.D. Lavanya", "RS - ECE"),
   "LAB": ("21ECC211L", "Devices and Digital IC Laboratory", "0-0-4-2", "Dr.S.Krishnakumar", "AP/ECE DS"),
  },
  cells=[
   ("Mon",3,4,"LAB -309/107",""),("Mon",6,6,"D",""),("Mon",7,7,"B",""),("Mon",8,8,"C",""),("Mon",9,9,"I",""),
   ("Tue",1,2,"LAB -309/107",""),("Tue",6,6,"C",""),("Tue",7,7,"D",""),("Tue",8,8,"E",""),("Tue",9,9,"A",""),
   ("Wed",1,1,"G - 401",""),("Wed",6,6,"I",""),("Wed",7,7,"E",""),("Wed",8,8,"A",""),("Wed",9,9,"D",""),
   ("Thu",1,2,"G-401",""),("Thu",3,4,"H-TB-106",""),("Thu",6,6,"A",""),("Thu",7,7,"C",""),("Thu",8,8,"B",""),("Thu",9,9,"E",""),
   ("Fri",1,1,"H - TB-106",""),("Fri",6,6,"F",""),("Fri",7,7,"A",""),("Fri",8,8,"B",""),("Fri",9,9,"C",""),
  ]),
 # ============ I-year file: 4 pages, 4 sections, academic year 2024-25 (STALE)
 "I-ECE-A": dict(
  source_file="I year Time Table SEEE.pdf", page=1, academic_year="2024-25", semester_type="Odd",
  year=1, semester=1, dept="ECE", venue="IST602 (per cell)", grid="GRID_2024_I_YEAR",
  approval_date="31/1/25; HOD 03/01/2025",
  subjects={
   "German": ("21LEH104T", "German", "2-1-0-3", "Mr. Selva", "German"),
   "E": ("21GNH101J", "Philosophy of Engineering", "1-0-2-2", "Dr. R. Aarthi", "AP/Phy"),
   "A": ("21MAB102T", "Advanced Calculus and Complex Analysis", "3-1-0-4", "Dr. R. Ragul", "AP / Maths"),
   "B": ("21CYB101J", "Chemistry", "3-1-2-5", "Dr. P. Pachamuthu", "AP/Che"),
   "C": ("21BTB102J", "Electronic System and PCB Design", "2-0-0-2", "Dr. U. Shajith Ali", "Asso.Prof/EEE"),
   "D": ("21CSS101J", "Programming for Problem Solving", "3-0-2-4", "Dr. A. Rama Prasath", "Asso.Prof/CA"),
   "Workshop": ("21MES101L", "Basic Civil and Mechanical Workshop", "0-0-4-2", "Dr. N.S. Balaji; Dr. M. Kumaran", "Asst.Prof/Mech"),
   "CDC": ("21PDM102L", "General Aptitude", "0-0-2-0", "Mr. Sivanandhan", "Communication Trainer"),
   "NSS": ("21GNM102L", "NSS", "0-0-2-0", "Dr. R. Manickam", "Physical Director"),
   "F": ("21BTB103T", "Biology", "2-0-0-2", "Dr. M. Jaya Priya", "AP/Biotech."),
  },
  cells=[
   ("Mon",1,1,"E IST602",""),("Mon",2,2,"E IST602",""),("Mon",3,3,"B IST602",""),("Mon",4,4,"A IST602",""),
   ("Mon",6,7,"Che lab",""),("Mon",8,8,"F IST710",""),("Mon",9,9,"CDC IST710",""),
   ("Tue",1,1,"C IST602",""),("Tue",2,2,"B IST602",""),("Tue",3,3,"A IST602",""),("Tue",4,4,"D IST602",""),("Tue",6,9,"Workshop (IST 20,21)",""),
   ("Wed",1,1,"B IST602",""),("Wed",2,2,"E IST602",""),("Wed",3,3,"D IST602",""),
   ("Wed",6,6,"PPS LAB",""),("Wed",7,7,"PPS LAB IST 618","handwritten"),("Wed",8,9,"PCB Lab IST 108","handwritten"),
   ("Thu",1,3,"German IST602",""),("Thu",4,4,"A IST602",""),("Thu",6,6,"CDC IST510",""),("Thu",7,7,"CDC IST510",""),("Thu",8,9,"NSS IST201","handwritten"),
   ("Fri",1,1,"D IST602",""),("Fri",2,2,"A IST602",""),("Fri",3,3,"C IST602",""),("Fri",4,4,"B IST602",""),("Fri",6,6,"F IST602",""),("Fri",7,9,"German IST626",""),
  ]),
 "I-ECE-B-EEE": dict(
  source_file="I year Time Table SEEE.pdf", page=2, academic_year="2024-25", semester_type="Odd",
  year=1, semester=1, dept="ECE+EEE (combined)", venue="IST602 (per cell)", grid="GRID_2024_I_YEAR",
  approval_date="3/1/25; HOD 03/01/2025",
  subjects={
   "German": ("21LEH104T", "German", "2-1-0-3", "Mr. Selva", "German"),
   "E": ("21GNH101J", "Philosophy of Engineering", "1-0-2-2", "Dr. R. Aarthi", "AP/Phy"),
   "A": ("21MAB102T", "Advanced Calculus and Complex Analysis", "3-1-0-4", "Dr. M. Deepa", "AP / Maths"),
   "B": ("21CYB101J", "Chemistry", "3-1-2-5", "Dr. N. Prabhu", "AP/Che"),
   "F": ("21BTB102J", "Electronic System and PCB Design (for ECE)", "", "Dr. U. Shajith Ali", "Asso.Prof./EEE"),
   "D": ("21CSS101J", "Programming for Problem Solving", "3-0-2-4", "Dr. A. Rama Prasath", "Asso.Prof./CA"),
   "Workshop": ("21MES101L", "Basic Civil and Mechanical Workshop", "0-0-4-2", "Dr. Modasir MD Khan; Mr.M.Karthikeyan", "AP/Mech"),
   "CDC": ("21PDM102L", "General Aptitude", "0-0-2-0", "Mrs. Thenmozhi", "Communication Trainer"),
   "NSS": ("21GNM102L", "NSS", "0-0-2-0", "Dr. R. Manickam", "Physical Director"),
   "C": ("21BTB103T", "Biology", "2-0-0-2", "Dr. M. Jaya Priya", "AP/Biotech."),
   "G": ("21EEC101J", "Electrical Circuits (for EEE)", "", "Dr.Dheepanchakkravarthy", "Asso.Prof/EEE"),
  },
  cells=[
   ("Mon",1,1,"CDC IST609",""),("Mon",2,2,"F IST710 / G IST520",""),("Mon",3,4,"Che lab",""),
   ("Mon",6,6,"E IST602",""),("Mon",7,7,"E IST602",""),("Mon",8,8,"B IST602",""),("Mon",9,9,"A IST602",""),
   ("Tue",1,4,"Workshop (IST 20,21)",""),("Tue",6,6,"C IST602",""),("Tue",7,7,"B IST602",""),("Tue",8,8,"A IST602",""),("Tue",9,9,"D IST602",""),
   ("Wed",1,1,"F IST710 / G IST520",""),("Wed",2,2,"PPS Lab IST 617","handwritten"),("Wed",3,3,"CDC IST510",""),("Wed",4,4,"CDC IST510","handwritten"),
   ("Wed",5,5,"PPS LAB IST618","handwritten"),("Wed",7,7,"B IST602",""),("Wed",8,8,"E IST602",""),("Wed",9,9,"D IST602",""),
   ("Thu",1,1,"NSS 201","handwritten"),("Thu",2,2,"NSS 201","handwritten"),("Thu",3,3,"C IST626",""),("Thu",4,4,"A IST710",""),
   ("Thu",6,6,"D IST602",""),("Thu",7,9,"German IST602",""),
   ("Fri",1,2,"PCB Lab/EC Lab IST 617","handwritten"),("Fri",4,6,"German IST626",""),("Fri",8,8,"B IST602",""),("Fri",9,9,"A IST602",""),
  ]),
 "I-ECE-DS": dict(
  source_file="I year Time Table SEEE.pdf", page=3, academic_year="2024-25", semester_type="EVEN (header) vs Sem I (body)",
  year=1, semester=1, dept="ECE-DS", venue="IST502 (per cell)", grid="GRID_2024_I_YEAR",
  approval_date="3/1/25",
  subjects={
   "German": ("21LEH104T", "German", "2-1-0-3", "Mr. Selva", "German"),
   "E": ("21GNH101J", "Philosophy of Engineering", "1-0-2-2", "Dr. R. Ramesh", "Asso.Prof./Mech"),
   "A": ("21MAB102T", "Advanced Calculus and Complex Analysis", "3-1-0-4", "Dr. Pandiyarajan", "AP / Maths"),
   "B": ("21CYB101J", "Chemistry", "3-1-2-5", "Dr. Ujjwala", "AP/Che"),
   "C": ("21BTB102J", "Electronic System and PCB Design", "2-0-0-2", "Dr. V.N.Senthil Kumaran", "Asso.Prof/ECE"),
   "D": ("21CSS101J", "Programming for Problem Solving", "3-0-2-4", "Mrs. R. Sharanya", "AP/CSE"),
   "Workshop": ("21MES101L", "Basic Civil and Mechanical Workshop", "0-0-4-2", "Dr. Sakthibalan; Dr. MD Modasir Khan", "AP/Mech"),
   "CDC": ("21PDM102L", "General Aptitude", "0-0-2-0", "Mr. Sivanandhan", "Communication Trainer"),
   "NSS": ("21GNM102L", "NSS", "0-0-2-0", "Dr. R. Manickam", "Physical Director"),
   "F": ("21BTB103T", "Biology", "2-0-0-2", "Dr.M.Maria Leena", "AP/Biotech."),
  },
  cells=[
   ("Mon",1,1,"F IST710",""),("Mon",2,2,"CDC",""),("Mon",3,4,"PCB Lab IST 617","handwritten"),
   ("Mon",6,6,"E IST502",""),("Mon",7,7,"E IST502",""),("Mon",8,8,"B IST502",""),("Mon",9,9,"A IST502",""),
   ("Tue",1,2,"Che lab",""),("Tue",3,3,"NSS 201","handwritten"),("Tue",4,4,"NSS 201","handwritten"),
   ("Tue",6,6,"C IST502",""),("Tue",7,7,"B IST502",""),("Tue",8,8,"A IST502",""),("Tue",9,9,"D IST502",""),
   ("Wed",1,1,"CDC IST510",""),("Wed",2,2,"CDC IST510",""),("Wed",3,3,"A IST710",""),
   ("Wed",5,6,"PPS lab / PPS LAB IST 617","handwritten"),("Wed",7,7,"B IST502",""),("Wed",8,8,"E IST502",""),("Wed",9,9,"D IST502",""),
   ("Thu",1,1,"F IST710",""),("Thu",2,2,"A IST510",""),("Thu",3,3,"D IST710",""),("Thu",4,6,"German IST502",""),
   ("Thu",8,8,"C IST502",""),("Thu",9,9,"B IST502",""),
   ("Fri",1,3,"German IST626",""),("Fri",4,4,"PPS LAB","faded"),("Fri",6,9,"Workshop (IST 20,21)",""),
  ]),
 "I-BIOTECH-B-BME": dict(
  source_file="I year Time Table SEEE.pdf", page=4, academic_year="2024-25", semester_type="EVEN (header) vs Sem I (body)",
  year=1, semester=1, dept="Biotech+BME (combined)", venue="IST702 (per cell)", grid="GRID_2024_I_YEAR",
  approval_date="3/1/25; HOD 03/01/2025",
  subjects={
   "Japanese": ("21LEH105T", "Japanese", "2-1-0-3", "Mr. Nadeem", "Japanese"),
   "E": ("21GNH101J", "Philosophy of Engineering", "1-0-2-2", "Dr. J. Ramya Parkavi", "AP/Phy"),
   "A": ("21MAB102T", "Advanced Calculus and Complex Analysis", "3-1-0-4", "Dr. R. Suresh", "AP / Maths"),
   "B": ("21CYB101J", "Chemistry", "3-1-2-5", "Dr. R. Logudurai", "AP/Che"),
   "D": ("21CSS101J", "Programming for Problem Solving", "3-0-2-4", "Dr. B. Chitradevi", "AP/CSE"),
   "C": ("21BTC105T", "Cell biology (for Biotech)", "2-0-0-2", "Dr. Daniel Paul", "AP/Biotech."),
   "Workshop": ("21MES101L", "Basic Civil and Mechanical Workshop", "0-0-4-2", "Dr.R.Manimaran; Dr.R.Ramesh", "AP/Mech; Asso.Prof/Mech"),
   "CDC": ("21PDM102L", "General Aptitude", "0-0-2-0", "Mr. Sivanandhan", "Communication Trainer"),
   "YOGA": ("21GNM101L", "Physical and Mental Health using Yoga", "0-0-2-0", "Ms. Balasivapriya", "Physical Instructor"),
   "F": ("21BTC101T", "Biochemistry (for Biotech)", "3-0-0-3", "Dr. M. Jaya Priya", "AP/Biotech."),
   "G": ("21BTB104T", "Biology: Human physiology and anatomy (only for Biomedical Engineering)", "2-0-0-2", "", ""),
  },
  cells=[
   ("Mon",1,1,"C IST520",""),("Mon",2,2,"YOGA",""),("Mon",3,3,"YOGA",""),("Mon",4,4,"F IST710 /G IST520",""),
   ("Mon",6,6,"E IST702",""),("Mon",7,7,"E IST702",""),("Mon",8,8,"A IST702",""),("Mon",9,9,"B IST702",""),
   ("Tue",1,1,"CDC IST710",""),("Tue",2,2,"CDC IST710",""),("Tue",3,3,"C IST520",""),("Tue",4,4,"F IST710",""),
   ("Tue",7,7,"B IST702",""),("Tue",8,8,"A IST702",""),("Tue",9,9,"D IST702",""),
   ("Wed",1,4,"Workshop (IST 20,21)",""),("Wed",6,6,"D IST702",""),("Wed",7,7,"B IST702",""),("Wed",8,8,"E IST702",""),("Wed",9,9,"D IST702",""),
   ("Thu",1,2,"Che lab",""),("Thu",3,3,"A IST710",""),("Thu",4,4,"C IST510/ G IST520",""),("Thu",6,6,"B IST702",""),("Thu",7,9,"Japanese IST702",""),
   ("Fri",1,1,"F IST702",""),("Fri",2,2,"CDC IST702",""),("Fri",3,3,"A IST702",""),("Fri",4,6,"Japanese IST702",""),
   ("Fri",8,8,"PPS LAB",""),("Fri",9,9,"PPS LAB",""),
  ]),
}
