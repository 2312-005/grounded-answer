# The Grounded Answer
Problem1:"The Grounded Answer"

## Requirements
- Python 3.11 or higher
- Git
- Ollama - Required model: llama3.2:1b-instruct-q3_K_M
- Internet connection for downloading Python packages and the embedding model

## Clone Repo
1. open the command prompt (window + r, cmd )

2. choose any directory in local  (eg:C:\Users\me>cd downloads)

3. then navigate to that directory (eg:C:\Users\me\Downloads>cd (any filenameeg:grounded-answer))

4. clone using "https://github.com/2312-005/grounded-answer.git(any file name(eg:grounded-answer))"

5. ensure current folder directory (eg: C:\Users\me\Downloads\grounded-answer>  ) 

6. " py -m venv .venv "  or  " python -m venv .venv " this is to initiate a virtual environment

7. paste " .venv\Scripts\activate " this activated virtual environment

8. the activated virtual environement must look like " (.venv) C:\Users\me\Downloads\grounded-answer> "

9. paste this " python -m pip install -r requirements.txt " to install the requirements, ensure sucessfull installation

10. In the same terminal " python -m uvicorn backend.main:app --reload " which starts the backend

## Ollama Setup
The Grounded Answer uses Ollama as the local language model service for generating grounded answers from the retrieved policy evidence.
### 1. Install Ollama
Download and install Ollama from:

https://ollama.com/download

After installation, make sure Ollama is running.

### 2. Download the Required Model
The application uses the following Ollama model:  llama3.2:1b-instruct-q3_K_M
 
Open Command Prompt or PowerShell and run: " ollama pull llama3.2:1b-instruct-q3_K_M "

Verify the Model - Run: " ollama list "
The output should contain: llama3.2:1b-instruct-q3_K_M
This confirms that the required model is installed.

11. open a new terminal for frontend (window + r), it shows(eg:C:\Users\me> ) change the directory "cd downloads" it looks like this(eg: C:\Users\me\Downloads> )

12. then navigate " cd grounded-answer " it should look like this (eg:C:\Users\me\Downloads>cd grounded-answer), the current folder directory

13. next activate virtual environment " .venv\Scripts\activate "

14. next paste " python -m http.server 5500 --directory frontend " 

15. Open the google browser and open ( " http://127.0.0.1:5500 ")

16. With simple UI design grounded answer interface, will open 

17. enter the question and click the "Ask Policy" button it checks the evidence it takes few seconds then answers

18. some sample question like 
           Question: " What is the residence condition? "
                     " What is the earnings disregard? "
                     " How many days does a recipient have to report a change of circumstances? "
                     " What are the basic eligibility conditions? "
                     " What is the sanction percentage? "
                     " What is the monthly income threshold for a household of 3? "
                     " What is the monthly income threshold for a household of 5? "
                     " What is the sanction percentage after the amendment? "
                     " What was the earnings disregard before the amendment? "
                     " What was the reporting period for a change of circumstances? "
                     " How long can a recipient be temporarily absent from Calder County? "

> Note: On the first run, the system may take a little time to download the embedding model and build the policy index from the supplied documents.
                             