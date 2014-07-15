#!/usr/bin/python

import sys
import os
import string
import datetime
from types import *

import smtplib
import ConfigParser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from CronUtils import SQLFileQuery
from CronUtils import HTMLFetch
from CronUtils import SysExec

docroot = '/root/crons'
cfgfile = 'Inmersa-cron.ini'

config = ConfigParser.ConfigParser()
if os.path.isfile(cfgfile):
   config.read(cfgfile)
elif os.path.isfile(docroot + '/' + cfgfile):
   config.read(docroot + '/' + cfgfile)
else:
   print "No config file (",cfgfile,") found in ",docroot
   sys.exit(0)

oFecha = datetime.datetime.today()
mainsection = 'General'

# Establecemos las variables por defecto
config.set('DEFAULT','fecha',str(oFecha.day)+'/'+str(oFecha.month)+'/'+str(oFecha.year))
config.set('DEFAULT','fechahora',str(oFecha.day)+'/'+str(oFecha.month)+'/'+str(oFecha.year)+' '+str(oFecha.hour)+':'+str(oFecha.minute))

aRawList = config.sections()
aSecList = list()
for i in range(len(aRawList)):
   if len(aRawList[i]):
      if aRawList[i] == mainsection: continue;
      seccion = aRawList[i]

      # Los no activos, ni los miramos
      if config.has_option(seccion,'activo'):
         act = config.get(seccion,'activo')
         if act in ('no','NO','nones','No','nO'): continue

      bHoraOK = False
      if not config.has_option(seccion,'hora'): bHoraOK = True
      else:
         hora = config.get(seccion,'hora')
         aTmp = hora.split(' ')
         for h in aTmp: 
            if str(oFecha.hour) == h :
               bHoraOK = True
               break;

      if bHoraOK and config.has_option(seccion,'diasemana'):
         bHoraOK = False
         diahoy = oFecha.weekday()+1
         tmpstr = config.get(seccion,'diasemana')
         aTmp = tmpstr.split(' ')
         if len(aTmp):
            for d in aTmp:
               if str(diahoy) == d:
                  bHoraOK = True
                  break;

      if bHoraOK and config.has_option(seccion,'dia'):
         bHoraOK = False
         diahoy = oFecha.day
         tmpstr = config.get(seccion,'dia')
         aTmp = tmpstr.split(' ')
         if len(aTmp):
            for d in aTmp:
               if str(diahoy) == d:
                  bHoraOK = True
                  break;

      if bHoraOK and config.has_option(seccion,'mes'):
         bHoraOK = False
         diahoy = oFecha.month
         tmpstr = config.get(seccion,'mes')
         aTmp = tmpstr.split(' ')
         if len(aTmp):
            for d in aTmp:
               if str(diahoy) == d:
                  bHoraOK = True
                  break;

      if bHoraOK:
         if config.has_option(seccion,'tipo'): aSecList.append(seccion)

#ruben
if  not len(aSecList):
        #print "Nothing to do at ",oFecha.hour
   	sys.exit(0)
'''
    	to = 'carlo@biomundo.com'
	gmail_user = 'carlos.biomundo@gmail.com'
	varfrom = 'carlos.biomundo@gmail.com'
	gmail_pwd = ''
	for (e,oBody) in dEmailList.items():
		print e, oBody
		smtpserver = smtplib.SMTP("smtp.gmail.com",587)
		smtpserver.ehlo()
		smtpserver.starttls()
		smtpserver.ehlo
		smtpserver.login(gmail_user, gmail_pwd)
   		print "enviando e-mail a : ",e
   		smtp.sendmail(varfrom,to,oBody.as_string())
   		#smtp.sendmail(varfrom,e,oBody.as_string())
		print 'done!'
		smtpserver.close()
'''

if config.has_option('General','remite'):
   varfrom = config.get('General','remite')
else: varfrom = 'IEmpresa-biomundo@biomundo'
if config.has_option('General','tema'):
   subject = config.get('General','tema')
else: subject = 'Informe de las '+str(oFecha.hour)
if config.has_option('General','smtp-server'):
   servidor_correo = config.get('General','smtp-server')
else: servidor_correo = 'mail.wol'

aEmailDef = list()
if config.has_option('General','email'):
   tmp = config.get('General','email')
   aTmp = tmp.split(' ')
   for e in aTmp: aEmailDef.append(e)

dEmailList = {}
for i in range(len(aSecList)):
   seccion = aSecList[i]

   dTipos = {
      'sql':SQLFileQuery,
      'html':HTMLFetch,
      'system':SysExec
      }
   tipo = config.get(seccion,'tipo')
   if tipo not in dTipos.keys(): 
      print "Tipo ",tipo," desconocido "
      continue;
   try:
      oI = dTipos[tipo](config,seccion)
   except Exception, e:
      oTmpMsg = MIMEText("Error en %s : %s " % (seccion,str(e)),'plain','ISO-8859-15')

   if not oI: continue
   oTmpMsg = oI.getMimeResult()
   if not oTmpMsg or (type(oTmpMsg) is not DictType and type(oTmpMsg) is not InstanceType) : continue

   aEmails = list()
   if config.has_option(seccion,'email'):
      tmp = config.get(seccion,'email')
      aTmp = tmp.split(' ')
      for e in aTmp: aEmails.append(e)
   else: aEmails = aEmailDef

   if type(oTmpMsg) is InstanceType:
      if aEmails and len(aEmails):
         for e in aEmails:
            if not dEmailList.has_key(e):
               dEmailList[e] = MIMEMultipart()
               dEmailList[e].add_header('Subject',subject)
               dEmailList[e].add_header('To',e)
            dEmailList[e].attach( oTmpMsg )
   else:
      """
         Si existe la opcion email en la seccion, ademas de a los indicados por la SQL (si hay) se manda
         email a estos.
      """
      for (e,oMsg) in oTmpMsg.items():
         if not dEmailList.has_key(e):
            dEmailList[e] = MIMEMultipart()
            dEmailList[e].add_header('Subject',subject)
            dEmailList[e].add_header('To',e)
         dEmailList[e].attach( oMsg )
         if config.has_option(seccion,'email'):
            for ee in aEmails:
               if ee == e: continue;
               if not dEmailList.has_key(ee):
                  dEmailList[ee] = MIMEMultipart()
                  dEmailList[ee].add_header('Subject',subject)
                  dEmailList[ee].add_header('To',ee)
               dEmailList[ee].attach( oMsg )

#for (e,oBody) in dEmailList.items():
#   print "enviando e-mail a : ",e
#   smtp.sendmail(varfrom,e,oBody.as_string())
#smtp.close()

to = 'carlos@biomundo.com'
user = 'carlos.biomundo@gmail.com'
#user = 'informes@biomundo.eu'
varfrom = 'carlos.biomundo@gmail.com'
#varfrom = 'informes@biomundo.eu'
pwd = '0rganic022.'
for (e,oBody) in dEmailList.items():
 	print e, oBody
        smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        #smtpserver = smtplib.SMTP("mail.biomundo.eu",587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(user, pwd)
        print "enviando e-mail a : ",e
        smtpserver.sendmail(varfrom,e,oBody.as_string())
        #smtp.sendmail(varfrom,e,oBody.as_string())
        print 'done!'
        smtpserver.close()