#!/usr/bin/python

from smtplib import SMTP
from datetime import date
import time
import sqlite3
import pygtk
pygtk.require("2.0")
import gtk
import os

### Variables ###
##
database_name = os.environ["HOME"] + '/.scrum'
from_email = ""
to_email = ""
sendmail_server = "localhost"
worker_name = "" # for example "Luis"
############

### Functions ###
##
def last_row(cursor):
  cursor.execute("SELECT task_id FROM sent_emails WHERE id = (SELECT MAX(id) FROM sent_emails);")
  row = cursor.fetchone()
  if row == None:
    return None
  else:
    return row[0]
################

### Callbacks ###
##
def enter_callback(self, window):
  print "Entry contents: %s\n" % self.get_text()
  query = "INSERT INTO tasks (description,time) values('" + self.get_text() + "',datetime('now'))"
  conn.execute(query)
  conn.commit()
  self.set_text("")
  window.hide_all()
  
def send_mail_callback(self):
  print "send"

def close_window_cb(self, daata = None):
  self.hide_all()
  return True

def new_text_cb(self, window):
  if not window.get_property("visible"):
    window.show_all()

def quit_cb(self, data = None):
  if data:
    data.set_visible(False)
    gtk.main_quit()

def popup_menu_cb(self, button, time, data = None):
  if button == 3:
    if data:
      data.show_all()
      data.popup(None, None, None, 3, time)

def send_email_cb(self, conn):
  cursor = conn.cursor()
  last_sent_id_task = last_row(cursor)
  if last_sent_id_task == None:
    cursor.execute("SELECT * FROM tasks;")
  else:
    cursor.execute("SELECT * FROM tasks WHERE id >" + str(last_sent_id_task) + ";")
  rows = cursor.fetchall()
  if len(rows) == 0:
    dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, "There are no pending emails")
    dialog.run()
    dialog.destroy()
  else:
    body = ""
    for row in rows:
      print "* %s" % row[1]
      body = body + "* " + row[1] + "\n"
    subject = "[SCRUM][" + date.today().strftime('%d %b %y') + "][" + worker_name + "] "
    header = 'To:' + to_email + '\n' + 'From: ' + from_email + '\n' + 'Subject:' + subject + ' \n'
    server = SMTP(sendmail_server)
    server.sendmail(from_email,to_email,header + body)
    print rows[-1][0]
    query = "INSERT INTO sent_emails (task_id,time) values('" + str(rows[-1][0])  + "',datetime('now'))"
    conn.execute(query)
    conn.commit()
 
#########

### GTK ########
##
window = gtk.Window(gtk.WINDOW_TOPLEVEL)

entry = gtk.Entry()
entry.set_width_chars(90)
entry.connect("activate", enter_callback, window)

hpaned = gtk.HPaned()
hpaned.add(entry)

window.set_title("Right now, I'm doing...")
window.set_resizable(False)
window.add(hpaned)
window.show_all()
window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
window.connect("delete-event", close_window_cb)

statusIcon = gtk.StatusIcon()

# Menu Item
menu = gtk.Menu()

# Menu Item
sendMenuItem = gtk.MenuItem("Send!")
menu.append(sendMenuItem)
separator = gtk.SeparatorMenuItem()
menu.append(separator)
menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
menuItem.connect('activate', quit_cb, statusIcon)
menu.append(menuItem)

# Status Icon
statusIcon.set_from_stock(gtk.STOCK_ABOUT)
statusIcon.set_tooltip("StatusIcon test")
statusIcon.connect('popup-menu', popup_menu_cb, menu)
statusIcon.set_visible(True)
statusIcon.connect('activate',new_text_cb, window)
############

### Main ##
if not os.path.isfile(database_name):
  conn = sqlite3.connect(database_name)
  conn.execute("CREATE TABLE tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, time TIMESTAMP)")
  conn.execute("CREATE TABLE sent_emails(id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, time TIMESTAMP)")
else:
  conn = sqlite3.connect(database_name)

sendMenuItem.connect('activate', send_email_cb, conn)

gtk.main()
##########
