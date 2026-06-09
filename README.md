# HKDSE ICT 2026 SBA Restaurant Booking System

A Python-based restaurant booking system developed as an HKDSE ICT School-based Assessment project.

This repository is shared as an educational reference for future ICT students who want to understand how a complete SBA project may be structured, documented, and implemented.

## Project Overview

This project simulates a restaurant booking system for **WaiWai’s Restaurant**. It includes both a graphical user interface version and a command-line version.

Main functions include:

- Customer account creation and login
- Restaurant table booking
- Booking modification and cancellation
- Availability checking
- Waiting list handling
- Admin management functions
- Basic file-based data storage
- Input validation and error handling

## Repository Contents

```text
.
├── MainBS_GUI_For_Marking.py      # GUI version, recommended for running the project
├── MainBookingSystem.py           # Command-line version
├── icon.png                       # Application icon
├── ICT SBA PDF 3.pdf              # Project documentation
└── README.md
```

## Requirements

- Python 3.10 or above
- Tkinter / Tk 8.6 or above

Tkinter is usually included with the standard Python installer from [python.org](https://www.python.org/).

## How to Run

### GUI Version

The GUI version is the recommended version.

```bash
python MainBS_GUI_For_Marking.py
```

Alternatively, open `MainBS_GUI_For_Marking.py` in VS Code and run it directly.

### Command-line Version

```bash
python MainBookingSystem.py
```

## First-time Setup

When the program is run for the first time, it may ask whether to create the required text files.

Choose **Yes** to continue.

The program will then generate the necessary data files automatically.

## Demo Admin Account

```text
User ID: LoveWaiWai
Password: iWANT5**
```

These credentials are for demonstration only and should not be reused in real systems.

## Notes for Students

This project is shared for reference only.

You may use this repository to learn about:

- How to structure a Python SBA project
- How GUI and CLI versions can be implemented
- How file handling can be used for simple data storage
- How validation, booking logic, and user roles can be designed
- How project documentation may be organised

However, you should not copy this project directly for your own SBA. Your own work should be original and should follow your school’s instructions and assessment requirements.

## Academic Integrity Notice

This repository is not intended to provide a ready-made SBA submission.

Students should not copy, submit, redistribute, or publish this project, in whole or in part, as their own assessment work.

Use this project as a learning reference only.

## Limitations

This project was developed for an HKDSE ICT SBA context. It is not intended for real commercial restaurant operations.

Known limitations may include:

- File-based storage instead of a real database
- Limited security protection
- Demo-level account system
- Local-only execution
- No online payment or real-time server support

## Possible Improvements

Future improvements could include:

- Replacing text files with SQLite
- Adding password hashing
- Improving the GUI layout
- Adding unit tests
- Adding better error logging
- Supporting multiple restaurants or branches
- Exporting booking records as CSV
- Adding a web-based interface

## License and Usage

Copyright © 2026 Linzin Leung. All rights reserved.

This repository is published for educational reference only. You may read the source code and project documentation to understand the design, implementation, and structure of an HKDSE ICT SBA project.

You may not copy, submit, redistribute, or publish this project, in whole or in part, as your own school-based assessment, coursework, or assessment work.

Students should design and implement their own original SBA project according to their school’s instructions and assessment requirements.

## Disclaimer

This project is an independent student project. It is not affiliated with, endorsed by, or officially provided by the Hong Kong Examinations and Assessment Authority, any school, or any examination body.
