## Ubelix Guide

1) Login VPN
2) Zip MIALab folder and put it on Ubelix --> scp /path/to/MIALab.zip <username>@submit01.unibe.ch:~/ (password will be asked)
2.1) you can also directly clone the project from git in the ubleix with git clone URL (use HTTPS not SSH) --> you have to use GIT bash terminal
3) login into ubelix --> ssh <username>@submit01.unibe.ch and insert password
4) Unzip the folder -->  unzip MIALab.zip
5) cd to the scripts folder
6) run the create_ubelix_env.sh --> sh create_ubelix_env.sh
7) exit the scripts folder with cd .. and run the requirements.txt --> pip install -r requirements.txt
8) enter again in the scripts folder and modify the script.sh --> nano script.sh (just change your mail at the bottom so you will recive an email when the job start/end/fail)
	ctrl + X to close and Y for save
9) submit the job --> sh script.sh output: Submitted batch job XXXXXX
10) see if the job is working --> squeue --me
	output:

             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
            578810     epyc2 MIALAB t mt19n014  R       0:31      1 bnode017



other) 

- delete a script --> scancel job_number (6 number)
- if there is a problem in the script and in the mail you recived a FAIL:
	check the slurm-XXXXXX.out file. you can open it directly in pycharm




## SSH pycharm

1) download JetBrains Gateway manually (EAP)
 https://www.jetbrains.com/help/pycharm/jetbrains-gateway.html#8fd0b9e1 (bottom of the page)
2) open and choose SSH connection
3) insert your username
	--> host: submit01.unibe.ch
	press enter and instert the passowrd
4) in project directory search for the MIALab folder under your username
5) start IDE and Connect (it will ast to create a login advice: use github )

--> now you can modify the code on Ubelix directly from pycharm
--> when you modify the code save it and than run it in the conscole --> sh script.sh



## Fetch the result


1) open a terminal without SSH connection
2) open the fetch_result.sh and modify REMOTE_USER, REMOTE_FOLDER and LOCAL_DESTINATION
	example:
		# Define variables
		REMOTE_USER="mt19n014"
		REMOTE_HOST="submit01.unibe.ch"
		REMOTE_FOLDER="/storage/homefs/mt19n014/MIALab/bin/mia-result" --> here you have to modify only your username
		LOCAL_DESTINATION="C:/Users/tmatt/Desktop"
		ZIP_FILE_NAME="mia-result.zip"

2) run the fetch_result script --> double click on it
	--> This means that you have to have the script in your local PC
	--> will ask your password 2 times



## link

https://mialab.readthedocs.io/en/latest/ubelix.html
https://unibe-cas-assignment.readthedocs.io/en/latest/assignment.ai.html