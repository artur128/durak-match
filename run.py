#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
from PyQt4 import QtGui, QtCore 
from benutzer import Ui_MainWindow as Dlg
from beamer import Ui_beamer as Dlg2
import sqlite3
try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	_fromUtf8 = lambda s: s



class spieler():
	def __init__(self,name,pid,points):
		self.name=name
		self.points=points
		self.prevgamers={}
		self.selected=False
		self.pid=pid
	def setprevgamer(self,spielername,anzahl):
		if spielername==self.name:
			return
		self.prevgamers.setdefault(spielername,anzahl)
	def __str__(self):
		return str(self.prevgamers)+" Points:"+str(self.points)
	def select(self):
		self.selected=True
	def deselect(self):
		self.selected=False
	def getprevgamercount(self,x):
		try:
			if type(x)==type(""):
				return self.prevgamers[x]
			else:
				return self.prevgamers[x.name]
		except:
			return 0
	def tmpshit(self,names):
		return len(filter(lambda x: self.getprevgamercount(x.name)>1,names))>0

def check_name(name):
	return (not (name=="")) and (" " not in name)

class Beamer(QtGui.QMainWindow, Dlg2):
	def __init__(self,conn_cursor,conn,mdlg):
		QtGui.QDialog.__init__(self)
		self.setupUi(self)
		self.conn_cursor=conn_cursor
		self.conn=conn
		self.mdlg=mdlg
		self.tables=[]
	def refresh_layout(self):
		players=int(self.mdlg.countplayers.text())
		import math
		columns=int(math.ceil(((float(self.mdlg.counttables.text()))**(0.5))))
		tables=int(self.mdlg.counttables.text())
		
		for x in self.tables:
			self.gridLayout.removeWidget(x)
			del x
		self.tables=[]
		c=0
		for t in range(0,tables):
				a = QtGui.QTableWidget(self.widget_3)
				a.setObjectName("a")
				a.setColumnCount(1)
				a.horizontalHeader().setStretchLastSection(True)
				a.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
				item = QtGui.QTableWidgetItem()
				item.setText("Tisch-"+str(t+1))
				a.setHorizontalHeaderItem(0, item)
				a.setRowCount(0)
				self.gridLayout.addWidget(a, c, t-c*columns, 1, 1)
				self.tables.append(a)
				if (t+1)%columns==0:
					c+=1
	def done_game(self):
		for x in range(0,len(self.games)):
			if self.tables[x].currentRow() == -1:
				QtGui.QMessageBox.question(self, 'Message',u"Nicht genug Duraks ausgewählt", QtGui.QMessageBox.Ok)
				return
		for x in range(0,len(self.tables)):
			for y in range(0,self.tables[x].rowCount()):
				if y != self.tables[x].currentRow():
					self.conn_cursor.execute("UPDATE players set points=points+1 where name=?",(unicode(self.tables[x].item(y,0).text()),))
					self.conn.commit()
				for z in range(0,self.tables[x].rowCount()):
					self.conn_cursor.execute("""INSERT INTO player_to_player (player1,player2) SELECT
					p1.id,p2.id from players as p1,players as p2 where p1.name=? and p2.name=?""",(
					unicode(self.tables[x].item(y,0).text()),
					unicode(self.tables[x].item(z,0).text())))
					self.conn.commit()
		self.refresh_button()
		self.mdlg.refresh_data()
	def refresh_button(self):
		self.refresh_layout()
		players=int(self.mdlg.countplayers.text())
		tables=int(self.mdlg.counttables.text())
		self.conn_cursor.execute("""SELECT * from players""")
		gamers=dict([(x['name'],spieler(x['name'],x['id'],x['points'])) for x in self.conn_cursor.fetchall()])

		for m in gamers.values():
			self.conn_cursor.execute("""SELECT p2.name as player2name,count(player2) as anzahl from players as p2,player_to_player as p where p.player1=? and p2.id=p.player2 GROUP BY player1,player2 ORDER BY player1""",(m.pid,))
			l=self.conn_cursor.fetchall()
			for k in l:
				m.setprevgamer(k['player2name'],k['anzahl'])
			print m,m.name

		games=[]
		while len(games)<tables and len(filter(lambda x: x.selected==False,sorted(gamers.values(),key=lambda x: x.points)))>1:
			best_gamer=filter(lambda x: x.selected==False,sorted(gamers.values(),key=lambda x: x.points))[0]
			best_gamer.select()
			to_play_with=[best_gamer]
			while len(to_play_with)<players and len(filter(lambda x: x.selected==False,sorted(gamers.values(),key=lambda x: x.points)))>0:
				x=filter(lambda x: x.selected==False,sorted(gamers.values(),key=lambda x: sum([x.getprevgamercount(m) for m in to_play_with])*1000+x.points ))[0]
				x.select()
				to_play_with.append(x)
			if len(to_play_with)>1:
				games.append(to_play_with)
		for g in range(0,len(games)):
			self.tables[g].setRowCount(len(games[g]))
			for p in range(0,len(games[g])):
				tmp=QtGui.QTableWidgetItem(games[g][p].name)
				tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.tables[g].setItem(p,0,tmp)
		self.games=games
				
		
		
		
class MeinDialog(QtGui.QMainWindow, Dlg): 
	def __init__(self,conn_cursor,conn): 
		QtGui.QDialog.__init__(self) 
		self.setupUi(self)
		self.conn_cursor=conn_cursor
		self.conn=conn
		self.ready=True
	def deleteplayer(self,a):
		if self.spieler.currentColumn() == 0:
			if QtGui.QMessageBox.Yes==QtGui.QMessageBox.question(self, 'Message',u"Spieler wirklich löschen?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No):
				self.conn_cursor.execute("""DELETE FROM players where id=? """,(int(self.spieler.item(self.spieler.currentRow(),0).text()),))
			self.refresh_data()
		
	def addplayer(self):
		newusername=unicode(self.newPlayerName.text())
		if check_name(newusername):
			self.newPlayerName.setText("")
			try:
				self.conn_cursor.execute("""INSERT INTO players (name,points) VALUES (?,?)""",(newusername,0))
				self.conn.commit()
			except:
				self.statusbar.showMessage("Fehler: SpielerName doppelt")
		else:
			self.statusbar.showMessage("Fehler: Kein Spieler-Name")
		self.refresh_data()
	def save(self,a,b):
		if self.ready and b==1:
			self.conn_cursor.execute("""UPDATE players set points=? where id=?""",(int(self.spieler.item(a,1).text()),int(self.spieler.item(a,0).text())))
			self.conn.commit()
			self.statusbar.showMessage("Saved "+str(a)+"-"+str(b))
	def refresh_data(self):
		self.ready=False
		self.conn_cursor.execute("""SELECT * FROM players ORDER BY id""")
		k=self.conn_cursor.fetchall()
		self.spieler.setRowCount(len(k))
		for i in range(0,len(k)):
			tmp=QtGui.QTableWidgetItem(str(k[i]['id']))
			tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
			self.spieler.setItem(i,0,tmp)
			self.spieler.setItem(i,1,QtGui.QTableWidgetItem(str(k[i]['points'])))
			tmp=QtGui.QTableWidgetItem(unicode(k[i]['name']))
			tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
			self.spieler.setItem(i,2,tmp)
		self.ready=True
		if self.spieler.currentRow()!=-1:
			self.update_playedwith(self.spieler.currentColumn(),self.spieler.currentRow(),-1,-1)
	def update_playedwith(self,a,b,aa,bb):
		player1id=self.spieler.item(a,0).text()
		self.conn_cursor.execute("""
SELECT 
	player2,count(player2) as anzahl, p2.name as  player2name
	FROM 
		players as p2, player_to_player 
	WHERE 
		player1=? and
		player2=p2.id
	GROUP BY 
		player1,player2
	ORDER BY
		player1""",(int(player1id),))
		k=self.conn_cursor.fetchall()

		self.games.setText("0")
		self.playedwith.setRowCount(max(len(k)-1,0))
		counteri=0
		for i in range(0,len(k)):
			if int(k[i]['player2'])==int(player1id):
				self.games.setText(str(k[i]['anzahl']))
			else:
				tmp=QtGui.QTableWidgetItem(str(k[i]['player2name']))
				tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.playedwith.setItem(counteri,0,tmp)
				tmp=QtGui.QTableWidgetItem(str(k[i]['player2']))
				tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.playedwith.setItem(counteri,1,tmp)
				tmp=QtGui.QTableWidgetItem(str(k[i]['anzahl']))
				tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.playedwith.setItem(counteri,2,tmp)
				counteri+=1
			
			

		

conn = sqlite3.connect("durak.sql",detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory=sqlite3.Row
conn.isolation_level = None

c= conn.cursor()
c.execute("pragma foreign_keys = on")
try:
	c.execute("SELECT count(*) FROM players")
	c.fetchone()
except:
	c.execute("CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, points INTEGER DEFAULT 0, actrive BOOLEAN DEFAULT True)")
	conn.commit()
	c.execute("CREATE TABLE player_to_player (player1 REFERENCES players(id) ON DELETE CASCADE , player2 REFERENCES players(id) ON DELETE CASCADE )")
	conn.commit()


app = QtGui.QApplication(sys.argv) 
dialog = MeinDialog(c,conn) 
beamer = Beamer(c,conn,dialog) 
dialog.refresh_data()
beamer.show()
dialog.show() 
beamer.refresh_layout()
sys.exit(app.exec_())
