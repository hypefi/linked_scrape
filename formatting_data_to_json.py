import datetime
import json
import fs

date =  datetime.datetime.now().isoformat()
print(date)


def formatting_data (data) :
    #formatting data   
    #print(data)
    #data =  json.dumps(data)
    datafor = []
    dataformatted =  {}
    dataformatted['title']= data.title
    dataformatted['jobtype']= data.employment_type
    dataformatted['location']= data.location
    dataformatted['company']= data.company
    dataformatted['remote']= 'true'
    dataformatted['description']= data.description
    dataformatted['url']= "https://www.linkedin.com/"+data.link
    if data.apply_link.isspace():
        dataformatted['contact']= dataformatted['url']
    dataformatted['contact']= data.apply_link
    dataformatted['userId']= 'qRofzWAQpCqJp9kXC'
    dataformatted['htmlDescription']= data.description_html
    dataformatted['createdAt']= date
    dataformatted['updatedAt']= date
    dataformatted['userName']= 'Anas Boukharta'
    datafor.append(dataformatted)

    print(datafor)

    with open('jobs.json', 'w') as outfile:
        json.dump(dataformatted, outfile)

