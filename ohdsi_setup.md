## OHDSI Quick start
So you decicided to take on an OHDSI project. Whats next?  To access this data you'll need to get set up in the OHDSI environment which can take some time. This quickstart guide is the information we would have found useful at the start of our project. 

## CITI Trainings
To even GET access to this environment you'll have to complete 3 [Citi Trainings](https://about.citiprogram.org/).  Create a login with your Northeastern credentials and complete the Conflict of Interest, Human Subjects Research and Social & Behavioral Responsible Conduct of Research.  These are lengthy so starting early is key. 
## VPN
If youre not already part of Northeasterns VPN work you'll need to do so by downloading it by following the instructions [Here](https://service.northeastern.edu/tech?id=kb_article_view&sysparm_article=KB0013983&sys_kb_id=a8310dcbc39ff290662dbc15990131b7&spa=1). This guide is very self explanatory and easy to follow
## Initial Login
Ensure you are connected to the VPN and have done your training with the OHDSI admin and start your workspace [here](https://ohdsi-lab.roux-ohdsi-prod.aws.northeastern.edu/#/my-workspaces). This should trigger an email with your Redshift credentials, and all other credentials, that you will use going forward. 
## Amazon Workspace 
After your training with the OHDSI admin (Jonah) you will need to download [Amazon Workspaces](https://clients.amazonworkspaces.com/). Your login will be Your Northeastern credentials (minus the @northeastern.edu).  You will also need to duo app for cross verification. 

## Virtual Machine 

Once oyu login using all of your workspace credentials you will be sent to a virtual machine which is where you'll have to do your work as the data is not available outside this environment. This machine includes VSCode & R for analysis and DBeaver for table storage

## DBeaver

To access the data start a new connection (Ctl+Shift+N) and click on Amazon Redshift. Your Redshift Username and Password was emailed to your previously, use that one NOT your northeastern credentials.  This will give you access into the data, where you can create views into your personal schema.  Note- You wont be able to use anybody elses schema so if you need to be consistent ensure you're using the same quereies. 

## Connecting GIT Hub 

You'll need to access GIT hub in the virutal machine, where the credentials on your local space won't be applicable.  The easiest way we found to do this was to set up a new SSH for the local machine following the guidelines on [GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) 
You can generate the ssh in the terminal using 
```
ssh-keygen -t ed25519 -C "your_email@example.com"
```

But will need to work in a bash terminal for all git related commands, Including cloning, pulling and any pushes you make. This includes connection with 

```
eval "$(ssh-agent -s)"
> Agent pid 59566
```
This should connect you in. The Github Documentation was helpful, as was Claude if you get stuck. 

You should now be able to use Python and make pushes like you were on your local machine. 