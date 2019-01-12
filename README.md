# UNO ACM Website

This repository holds all the source code for the UNO ACM Website. The only thing not here is the database file. Since this website will not have much activity, the database will be a sqlite file. This may need to change in the future.

# Installation and Run Guide

The first thing you'll have to do is clone this repository.

```
git clone https://github.com/unoacm/Website.git
```

Since this website is using Python, it is recommended to use a virtual environment with this. The easiest way to set it up is to have a folder containing your virtual envrionment and whatever folder comes from the git clone, such as:

```
WebsiteProject
  |
  --- env (virtual environment)
  |
  --- Website (git clone)
```

Once you have made your virtual environment, you will want to activate it. Then you want to use pip to install all the requirements inside of the requirements.txt file:

```
pip install -r requirements.txt
```

After that you should be able to run it:

```
python website.py
```
or
```
py website.py
```

## Needed Environmental Variables

FLASK_ENV : 'development', 'production' : This tells flask whether the app is in development or production. In production a different database name/type will be used.

More installation instructions might appear as this application gets ready for production.