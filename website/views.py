from flask import Blueprint, render_template, request, flash, Markup

from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDF, RDFS
from pyshacl import validate

def remove(string):
    return string.replace(" ", "")

def getLocal(uri):
    pos = -1
    pos = uri.rfind('#')
    if pos < 0 :
        pos = uri.rfind('/')
    #if pos < 0 :
     #   pos =  uri.rindex(':')
    return uri[pos+1:]
    

views = Blueprint('views',__name__)

@views.route('/')
def home():
    return render_template('home.html')


@views.route('/riskregister')
def airima():
    return render_template('riskregister.html')


@views.route('/highrisk', methods=['GET', 'POST'])
def highrisk():
    #----------------------Getting instances from VAIR-----------------
    vair_use = Graph()
    vair_use.parse("https://raw.githubusercontent.com/DelaramGlp/vair/main/vair-useofai.ttl", format="turtle")

    vair_ai=Graph()
    vair_ai.parse("https://raw.githubusercontent.com/DelaramGlp/vair/main/vair-ai.ttl", format="turtle")

    vair_stakeholder=Graph()
    vair_stakeholder.parse("https://raw.githubusercontent.com/DelaramGlp/vair/main/vair-stakeholder.ttl", format="turtle")

    #------------domains-----------
    domain_query="""
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX airo:<https://w3id.org/airo#>
                    SELECT ?domain ?label
	                WHERE {?domain rdfs:subClassOf* airo:Domain.
                    ?domain  skos:prefLabel ?label .}
                    order by asc(UCASE(str(?domain)))"""
   
    domains = []
    for row in vair_use.query(domain_query):
        term= getLocal(str(row.domain))
        label = getLocal(str(row.label))
        domains.append((term, label))
      
    #------------purposes-----------
    purpose_query="""
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX airo:<https://w3id.org/airo#>
                    SELECT ?purpose ?label
	                WHERE {?purpose rdfs:subClassOf* airo:Purpose.
                           ?purpose  skos:prefLabel ?label .
                   }order by asc(UCASE(str(?purpose)))"""
   
    purposes = []
    for row in vair_use.query(purpose_query):
        term= getLocal(str(row.purpose))
        label = getLocal(str(row.label))
        purposes.append((term, label))

    #------------capabilities----------- 
    capability_query="""
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX airo:<https://w3id.org/airo#>
                    SELECT ?capability ?label
	                WHERE {?capability rdfs:subClassOf* airo:Capability.
                            ?capability skos:prefLabel ?label .
                    } order by asc(UCASE(str(?capability)))

"""
    capabilities = []
    for row in vair_ai.query(capability_query):
        term= getLocal(str(row.capability))
        label = getLocal(str(row.label))
        capabilities.append((term, label))

    #------------users-----------
    user_query="""
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX airo:<https://w3id.org/airo#>
                    SELECT ?user ?label
	                WHERE {?user rdfs:subClassOf* airo:AIUser.
                            ?user  skos:prefLabel ?label .
                    } order by asc(UCASE(str(?user)))

"""
    users = []
    for row in vair_stakeholder.query(user_query):
        term= getLocal(str(row.user))
        label = getLocal(str(row.label))
        users.append((term, label))

 

     #------------subjects-----------
    subject_query="""
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX airo:<https://w3id.org/airo#>
                    SELECT ?subject ?label
	                WHERE {?subject rdfs:subClassOf* airo:AISubject.
                            ?subject  skos:prefLabel ?label .
                    } order by asc(UCASE(str(?subject)))

"""
    subjects = []
    for row in vair_stakeholder.query(subject_query):
        term= getLocal(str(row.subject))
        label = getLocal(str(row.label))
        subjects.append((term, label))
    
    
   # print([getLocal(str(row.subject)) for row in vair_stakeholder.query(subject_query)])


    #----------------------Getting user's input---------------------- 
    if request.method == 'POST':

        system = remove(request.form.get('system'))
        systemUri = URIRef('http://example.com/ns#' + system)

        #print("___"+systemUri)

        vair_domain = request.form.get('domain')
        vair_domainUri = URIRef('https://w3id.org/vair#' + vair_domain)
        domainUri = URIRef('http://example.com/ns#' + system +'domain')
       
    
        vair_purpose = request.form.get('purpose')
        vair_purposeUri = URIRef('https://w3id.org/vair#' + vair_purpose)
        purposeUri = URIRef('http://example.com/ns#' + system +'purpose')
        
        
        vair_capability = request.form.get('capability')
        vair_capabilityUri = URIRef('https://w3id.org/vair#' + vair_capability)
        capabilityUri = URIRef('http://example.com/ns#' + system +'capability')
        #print("___"+capabilityUri)

        vair_user = request.form.get('user')
        vair_userUri = URIRef ('https://w3id.org/vair#' + vair_user)
        userUri = URIRef ('http://example.com/ns#' + system +'user')

        vair_subject = request.form.get('subject')
        vair_subjectUri = URIRef ('https://w3id.org/vair#' + vair_subject)
        subjectUri = URIRef('http://example.com/ns#' + system +'subject')


#----------------------Creating RDF Graph from the user's input---------------------- 
        g = Graph()
        empty = False
        airo = Namespace('https://w3id.org/airo#')
        vair = Namespace('https://w3id.org/vair#')
        ex = Namespace('http://example.com/ns#')
        
        g.bind("airo", airo)
        g.bind("vair", vair)
        g.bind("ex",ex)
    
        g.add((systemUri,RDF.type,URIRef("https://w3id.org/airo#AISystem"))) 
        if vair_domain =="None" and vair_purpose=="None" and vair_capability=="None" and vair_user=="None" and vair_subject=="None":
            empty= True
        if vair_domain != "Other":
            g.add((systemUri, URIRef("https://w3id.org/airo#isAppliedWithinDomain"),domainUri))
            g.add((domainUri,RDF.type,vair_domainUri))
        else:
            g.add((systemUri, URIRef("https://w3id.org/airo#isAppliedWithinDomain"),domainUri))
            g.add((domainUri,RDF.type,URIRef("http://w3id.org/airo#Domain")))

        if vair_purpose != "Other" :    
            g.add((systemUri, URIRef("https://w3id.org/airo#hasPurpose"), purposeUri))
            g.add((purposeUri, RDF.type, vair_purposeUri))
        else:
            g.add((systemUri, URIRef("https://w3id.org/airo#hasPurpose"),purposeUri))
            g.add((purposeUri,RDF.type,URIRef("http://w3id.org/airo#Purpose")))    

        if vair_capability != "Other":    
            g.add ((systemUri, URIRef("https://w3id.org/airo#hasCapability"), capabilityUri))
            g.add((capabilityUri, RDF.type, vair_capabilityUri))
        else:
            g.add((systemUri, URIRef("https://w3id.org/airo#hasCapability"),capabilityUri))
            g.add((capabilityUri,RDF.type,URIRef("http://w3id.org/airo#Capability")))      
            
        if vair_user != "Other":
            g.add ((systemUri, URIRef("https://w3id.org/airo#isUsedBy"), userUri))
            g.add((userUri, RDF.type, vair_userUri))
        else:
            g.add((systemUri, URIRef("https://w3id.org/airo#isUsedBy"),userUri))
            g.add((userUri,RDF.type,URIRef("http://w3id.org/airo#Stakeholder")))      

        if vair_subject != "Other":    
            g.add((systemUri, URIRef("https://w3id.org/airo#hasAISubject"), subjectUri))
            g.add((subjectUri, RDF.type, vair_subjectUri))
        else:
            g.add((systemUri, URIRef("https://w3id.org/airo#hasAISubject"),subjectUri))
            g.add((subjectUri,RDF.type,URIRef("http://w3id.org/airo#Stakeholder")))    
            
        dg = g.serialize(format ='turtle')
        print(dg)

        spec = Markup("<p> Domain:" + vair_domain + "<br> Purpose: " + vair_purpose + "<br>Capability: " + vair_capability + "<br>User: "+ vair_user + "<br>Subject: " + vair_subject +"</p>")
        print(spec)
        #----------------------SHACL shape----------------------
        sg = Graph() #shacl graph
        sg.parse("https://raw.githubusercontent.com/DelaramGlp/airo/main/high-risk-shacl/shapes-updated.ttl", format="turtle")

        conforms, report, message = validate(dg, shacl_graph=sg, advanced=True, debug=False)
        #print (message)

        #Print sh:message (AI Act reference) if the system is high-risk
        if empty==True :
            flash("Please Provide more details about your AI system")    
        elif conforms == False:
             resultMessage = report.objects(predicate=URIRef("http://www.w3.org/ns/shacl#resultMessage"))
             for m in resultMessage:
                 flash ("Your AI system is likely to be "+ m + spec , category='high-risk')
        else:
            flash("The following AI System is likely to be Not High-Risk: " +spec )
   
            
      

    #return render_template('highrisk.html', domains = domains, purposes = purposes, capabilities = capabilities, users = users)
    return render_template('highrisk.html', domains=domains, purposes = purposes, capabilities = capabilities, users = users, subjects = subjects)