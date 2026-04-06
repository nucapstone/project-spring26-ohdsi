## OHDSI Quick start
So you decicided to take on an OHDSI project. What's next? To access this data you'll need to get set up in the OHDSI environment which can take some time. This quickstart guide is the information we would have found useful at the start of our project. 

## CITI Trainings
To even GET access to this environment you'll have to complete 3 [Citi Trainings](https://about.citiprogram.org/). Create a login with your Northeastern credentials and complete the Conflict of Interest, Human Subjects Research, and Social & Behavioral Responsible Conduct of Research. These are lengthy so starting early is key.

## VPN
If you're not already part of Northeastern's VPN work you'll need to do so by downloading it by following the instructions [here](https://service.northeastern.edu/tech?id=kb_article_view&sysparm_article=KB0013983&sys_kb_id=a8310dcbc39ff290662dbc15990131b7&spa=1). This guide is very self explanatory and easy to follow.

## Initial Login
Ensure you are connected to the VPN, have done your training with the OHDSI admin, and are ready to start your workspace [here](https://ohdsi-lab.roux-ohdsi-prod.aws.northeastern.edu/#/my-workspaces). This should trigger an email with your Redshift credentials, and all other credentials, that you will use going forward.

## Amazon Workspace 
After your training with the OHDSI admin (currently Jonah Bradenday) you will need to download [Amazon Workspaces](https://clients.amazonworkspaces.com/). Your login will be Your Northeastern credentials (minus the @northeastern.edu). You will also need the Duo App for authentication.

## Virtual Machine 
Once you login using all of your workspace credentials, you will be sent to a virtual machine which is where you'll have to do your work as the data is not available outside this environment. This machine includes VSCode & R for analysis and DBeaver for table storage.

## DBeaver
To access the data, start a new connection (Ctl+Shift+N) and click on Amazon Redshift. Your Redshift Username and Password was emailed to your previously; Use those credentials, NOT your northeastern credentials. This will give you access into the data, where you can create table views in your personal schema. Note: You won't be able to use anybody else's schema, so ensure reproducibility with deterministic SQL queries or setting your seed/state when querying.

## Connecting GitHub
You'll need to access GitHub in the virutal machine, where the credentials on your local space won't be applicable. The easiest way we found to do this was to set up a new SSH for the local machine following the guidelines on [GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) 
You can generate the ssh in the terminal using 
```
ssh-keygen -t ed25519 -C "your_email@example.com"
```

You will need to work in a bash terminal for all git related commands, including cloning, pulling, and any pushes you make. This includes connection with 

```
eval "$(ssh-agent -s)"
> Agent pid 59566
```

This should connect you. The Github Documentation was helpful, as was Claude if you get stuck.

You should now be able to use Python and connect to GitHub as if you were on your local machine.