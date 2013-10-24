#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
from PyQt4 import QtGui, QtCore 
from benutzer import Ui_MainWindow as mainwindow
from beamer import Ui_beamer as beamer_window
import sqlite3
import math




class BeamerWindow(QtGui.QMainWindow, beamer_window):
	def __init__(self,game):
		QtGui.QDialog.__init__(self)
		self.setupUi(self)
		self.game=game
		self.tables=[]
		self.refresh_layout()
	def refresh_layout(self):
		players=self.game.get_players_per_table()
		columns=int(math.ceil(float(self.game.get_tables())**(0.5)))
		tables=int(self.game.get_tables())
		
		for x in self.tables:
			self.gridLayout.removeWidget(x)
			x.deleteLater()
			del x
		self.tables=[]
		c=0
		for t in range(0,tables):
				a = QtGui.QTableWidget(0,0,self.widget_3)
				a.setObjectName("a-"+str(t))
				a.setColumnCount(3)
				a.horizontalHeader().setStretchLastSection(True)
				a.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
				a.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
				a.setSortingEnabled(True)
				item = QtGui.QTableWidgetItem()
				item.setText("Tisch-"+str(t+1))
				a.setHorizontalHeaderItem(2, item)

				item = QtGui.QTableWidgetItem()
				item.setText("num")
				a.setHorizontalHeaderItem(0, item)

				item = QtGui.QTableWidgetItem()
				item.setText("#")
				a.setHorizontalHeaderItem(1, item)

				a.setColumnHidden(0,True)
				a.horizontalHeader().setStretchLastSection(True)
				a.setSortingEnabled(True)
				a.sortByColumn(1,QtCore.Qt.DescendingOrder)
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
		o=self.game.get_tables_allocation()
		for a in range(0,len(o)):
			self.tables[a].setSortingEnabled(False)
			self.tables[a].setRowCount(len(o[a]))
			for x in range(0,len(o[a])):
				tmp=QtGui.QTableWidgetItem(o[a][x]['pid'])
				tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.tables[a].setItem(x,0,tmp)
				tmp=QtGui.QTableWidgetItem("0")
				self.tables[a].setItem(x,1,tmp)
				tmp=QtGui.QTableWidgetItem(o[a][x]['name'])
				tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.tables[a].setItem(x,2,tmp)
			self.tables[a].setSortingEnabled(True)


				
		
		
		
class MainWindow(QtGui.QMainWindow, mainwindow): 
	def __init__(self,game): 
		QtGui.QDialog.__init__(self) 
		self.setupUi(self)
		self.game=game
		self.not_refresh_data=True
		self.countplayers.setValue(self.game.get_players_per_table())
		self.counttables.setValue(self.game.get_tables())
		self.spieler.setColumnHidden(0,True)
		self.spieler.sortByColumn(1,QtCore.Qt.DescendingOrder)
		self.spieler.setSortingEnabled(True)
		self.playedwith.setColumnHidden(1,True)
		self.playedwith.sortByColumn(2,QtCore.Qt.DescendingOrder)
		self.playedwith.setSortingEnabled(True)
		self.refresh_player_list()
	def deleteplayer(self,a):
		if self.spieler.currentColumn() == 2:
			if QtGui.QMessageBox.Yes==QtGui.QMessageBox.question(self, 'Message',u"Spieler wirklich löschen?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No):
				self.game.delete_player(int(self.spieler.item(self.spieler.currentRow(),0).text()))
		self.refresh_player_list()
	def addplayer(self):
		try:
			self.game.add_player(unicode(self.newPlayerName.text()))
		except:
			self.statusbar.showMessage(u"Fehler: Nicht hinzugefügt")
		else:
			self.statusbar.showMessage(u"Fehler: Nicht hinzugefügt")
			self.newPlayerName.setText("")
		self.refresh_player_list()
	def players_per_table_changed(self,l):
		self.game.set_players_per_table(int(l))
	def tables_changed(self,l):
		self.game.set_tables(int(l))
	def cell_changed(self,a,b):
		if self.not_refresh_data and b==1:
			self.game.change_player_points(int(self.spieler.item(a,0).text()),int(self.spieler.item(a,1).text()))
			self.statusbar.showMessage("Saved "+str(a)+"-"+str(b))
			self.refresh_player_list()
	def refresh_player_list(self):
		self.not_refresh_data=False
		k=self.game.get_all_players()
		print k
		self.spieler.setRowCount(len(k))
		self.spieler.setSortingEnabled(False)
		for i in range(0,len(k)):
			tmp=QtGui.QTableWidgetItem(unicode(k[i]['id']))
			tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
			self.spieler.setItem(i,0,tmp)
			self.spieler.setItem(i,1,QtGui.QTableWidgetItem("%02d"%k[i]['points']))
			tmp=QtGui.QTableWidgetItem(unicode(k[i]['name']))
			tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
			self.spieler.setItem(i,2,tmp)
		self.spieler.setSortingEnabled(True)
		self.not_refresh_data=True
		if self.spieler.currentRow()!=-1:
			self.update_playedwith(self.spieler.currentColumn(),self.spieler.currentRow(),-1,-1)
	def update_playedwith(self,a,b,aa,bb):
		player1id=self.spieler.item(a,0).text()
		k=self.game.get_played_with_for_player(int(player1id))

		self.games.setText("0")
		self.playedwith.setRowCount(max(len(k)-1,0))
		counteri=0
		self.playedwith.setSortingEnabled(False)
		for i in range(0,len(k)):
			if int(k[i]['p2id'])==int(player1id):
				self.games.setText(str(k[i]['matches']))
			else:
				tmp=QtGui.QTableWidgetItem(str(k[i]['player2name']))
				tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.playedwith.setItem(counteri,0,tmp)
				tmp=QtGui.QTableWidgetItem(str(k[i]['p2id']))
				tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.playedwith.setItem(counteri,1,tmp)
				tmp=QtGui.QTableWidgetItem("%02d"%k[i]['matches'])
				tmp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.playedwith.setItem(counteri,2,tmp)
				counteri+=1
		self.playedwith.setSortingEnabled(True)
			

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

class Game():
	def get_tables_allocation(self):
		self.db_cursor.execute("""SELECT * from players order by points""")
		gamers=[spieler(x['name'],x['id'],x['points']) for x in self.db_cursor.fetchall()]

		for m in gamers:
			for x in self.get_played_with_for_player(m.pid):
				m.setprevgamer(x['player2name'],int(x['matches']))

		games=[]
		while len(games)<self.tables and len(filter(lambda x: x.selected==False,reversed(sorted(gamers,key=lambda x: x.points))))>1:
			best_gamer=filter(lambda x: x.selected==False,reversed(sorted(gamers,key=lambda x: x.points)))[0]
			best_gamer.select()
			to_play_with=[best_gamer]
			while len(to_play_with)<self.players_per_table and len(filter(lambda x: x.selected==False,reversed(sorted(gamers,key=lambda x: x.points))))>0:
				x=filter(lambda x: x.selected==False,reversed(sorted(gamers,key=lambda x: sum([x.getprevgamercount(m) for m in to_play_with])*1000+x.points )))[0]
				x.select()
				to_play_with.append(x)
			if len(to_play_with)>1:
				games.append(to_play_with)
		self.games=games
		return [[{'name':y.name,'pid':y.pid,'points':y.points} for y in x]for x in games]
	def set_players_per_table(self,i):
		self.players_per_table=i
	def get_players_per_table(self):
		return self.players_per_table
	def set_tables(self,i):
		self.tables=i
	def get_tables(self):
		return self.tables
	def get_played_with_for_player(self,pid):
		self.db_cursor.execute("""
SELECT 
	player2 as p2id,count(player2) as matches, p2.name as  player2name
FROM 
		players as p2, player_to_player 
WHERE 
		player1=? and
		player2=p2.id
GROUP BY 
		player1,player2
ORDER BY
		player1""",(pid,))
		k=self.db_cursor.fetchall()
		return [dict(x) for x in k]
	def get_all_players(self):
		self.db_cursor.execute("""SELECT * FROM players ORDER BY id""")
		k=self.db_cursor.fetchall()
		return [dict(x) for x in k]
	def change_player_points(self,pid,newpoints):
		self.db_cursor.execute("""UPDATE players set points=? where id=?""",(newpoints,pid))
		self.db_connection.commit()
	def add_player(self,newplayername):
		if not ( (not (newplayername=="")) and (" " not in newplayername)):
			raise Exception("Not Valid username")
		self.db_cursor.execute("""INSERT INTO players (name,points) VALUES (?,?)""",(newplayername,0))
		self.db_connection.commit()
	def delete_player(self,pid):
		self.db_cursor.execute("""DELETE FROM players where id=? """,(pid,))
		self.db_connection.commit()
	def __init__(self):
		self.players_per_table=3
		self.tables=8
		self.db_connection = sqlite3.connect("durak.sql",detect_types=sqlite3.PARSE_DECLTYPES)
		self.db_connection.row_factory=sqlite3.Row
		self.db_connection.isolation_level = None
		self.db_cursor = self.db_connection.cursor()
		self.db_cursor.execute("pragma foreign_keys = on")
		try:
			self.db_cursor.execute("SELECT count(*) FROM players")
			self.db_cursor.fetchone()
		except:
			self.db_cursor.execute("""
CREATE TABLE 
	players 
		(
			id INTEGER PRIMARY KEY,
			name TEXT NOT NULL UNIQUE,
			points INTEGER DEFAULT 0,
			active BOOLEAN DEFAULT True
		)""")
			self.db_connection.commit()
			self.db_cursor.execute("""
CREATE TABLE 
	player_to_player 
		(
			player1 REFERENCES players(id) ON DELETE CASCADE, 
			player2 REFERENCES players(id) ON DELETE CASCADE 
		)""")
			self.db_connection.commit()

			
if __name__ == "__main__":
	game=Game()
	app = QtGui.QApplication(sys.argv) 
	mw = MainWindow(game) 
	bw = BeamerWindow(game) 
	bw.show()
	mw.show() 
	sys.exit(app.exec_())
