## WiTHackathon2020-CountOnUs_Application

An application designed to cater the basic necessities of the victims of COVID-19 . Kindness doesn't need proximity, a simple click will do it. Let's click !

## Instructions

To run this application in local, you need to follow these instructions.

1. Create a workspace if you have not done so already.
2. Fork this repository by clicking the "fork" button in the top right.
3. Open a terminal and enter this repository.
4. You should have an account created on IBM Cloud. For now you can use the Lite plan.
5. The application is using IBM's Cloudant database.
6. For connecting local with the database, login to your IBM Cloud account and create a IBM Cloudant resource.
7. Create Service Credentials for the Cloudant resource that you have created.
8. Click view credentials and paste the username,password & host values in vcap-local.json.
9. Now your local is connected with Cloudant Database.
10. For python3, run these commands in your terminal
    ```
    pip3 install -r requirements.txt
    python3 main.py
    ```
    For python2, run
    ```
    pip install -r requirements.txt
    python main.py
    ``` 
 
11. View the application at: http://localhost:8000.

## Prerequisites

For running this application in local you need to install:
1. Python2 / Python3
2. Flask


## Deployment

The application is deployed on IBM Cloud Foundry


## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* IBM
