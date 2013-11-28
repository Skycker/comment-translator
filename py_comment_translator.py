import sys
import os
import re 

from PyQt4 import QtCore, QtGui, uic

comment_list = []
translated_comments = []
code = ''
i = 0 # counter of comments

class MainForm(QtGui.QMainWindow):
    '''Class for GUI '''

    def __init__(self):
        super(MainForm, self).__init__()
        
        homeDir = os.path.dirname(sys.argv[0])
        uic.loadUi(homeDir + '/mainForm.ui', self)

        # Connect events and its handlers together
        self.actionOpen.triggered.connect(self.open_menuClicked)
        self.actionSave.triggered.connect(self.save_menuClicked)
        self.actionUndo.triggered.connect(self.undo_menuClicked)
        self.actionRedo.triggered.connect(self.redo_menuClicked)
        self.actionOpen.setShortcut('Ctrl+O')
        self.actionSave.setShortcut('Ctrl+S')
        
        # Handlers of pressed buttons
        QtCore.QObject.connect(self.change_pbtn, QtCore.SIGNAL('clicked()'),  
           self.change_pbtnClicked)
        QtCore.QObject.connect(self.skip_pbtn, QtCore.SIGNAL('clicked()'),  
           self.skip_pbtnClicked)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Important!',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def open_menuClicked(self):
        """Opening file """
        global comment_list, code, i
        # null counter of comments
        # it will coll if we edit 2nd and etc file
        i = 0

        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        code = open(file_path).read()
        self.filePath_lbl.setText(file_path) 

        # Find comments and put into list
        reg1 = re.compile('#.*')
        reg2 = re.compile('\'\'\'.*?\'\'\'', re.S)
        reg3 = re.compile('\"\"\".*?\"\"\"', re.S)
        list1 = reg1.findall(code)
        list2 = reg2.findall(code)
        list3 = reg3.findall(code)
        comment_list = list1 + list2 + list3

        self.show_new_comment()

    def save_menuClicked(self):
        """Save file """
        # first, change comments into translated ones
        global code
        for i in range(len(translated_comments)):
            if translated_comments[i] is None:
                continue
            else:
                if comment_list[i][0] == '#':
                    translation = '# ' + translated_comments[i]
                elif comment_list[i][0] == '\'':
                    if '\n' in comment_list[i]:
                        translation = '\'\'\'%s \n\'\'\''  %translated_comments[i]
                    else:
                        translation = '\'\'\'%s \'\'\''  %translated_comments[i]
                elif comment_list[i][0] == '\"':
                    if '\n' in comment_list[i]:
                        translation = '\"\"\"%s \n\"\"\"'  %translated_comments[i]
                    else:
                        translation = '\"\"\"%s \"\"\"'  %translated_comments[i]
                code = code.replace(comment_list[i], translation)

        # and put it in file
        file_name = QtGui.QFileDialog.getSaveFileName(self, 'Save file',)
        my_file = open(file_name, 'w')
        my_file.write(code)
        my_file.close()

    def undo_menuClicked(self):
        """Go back on 1 comment """
        global i
        if i > 0: 
            i -= 1
            self.show_new_comment()

    def redo_menuClicked(self):
        """Go toward on 1 comment """
        global i
        if i < len(translated_comments):
            i += 1
            self.show_new_comment()

    def change_pbtnClicked(self):
        """Changing current comment into typed text """
        global i, code, comment_list, translated_comments

        # make translation of current comment
        if self.textEdit_after.toPlainText():
            translation = self.textEdit_after.toPlainText()
            
            if i == len(translated_comments):
                translated_comments.append(translation)
            else:
                translated_comments[i] = translation
            
            i += 1
            
            if i < len(comment_list):
                self.show_new_comment()
            else:
                self.textEdit_before.clear()
                self.textEdit_after.clear()
            
            #print('//----------------')
            #print(code)

    def skip_pbtnClicked(self):
        """ Skipping current comment. 
        (for people who leave commented code at project) 
        """
        global i, translated_comments

        # If we don't want to translate or tool ask us to translate code
        if i == len(translated_comments):
            translated_comments.append(None)

        i += 1
        if i < len(comment_list):
            self.show_new_comment()
        else:
            self.textEdit_before.clear()

    def show_new_comment(self):
        pos = code.find(comment_list[i])
        self.textEdit_before.clear()

        # find the 3rd line before current comment
        start = None
        j = pos
        q = 0
        while j != 0:
            if code[j] == '\n':
                if q == 3:
                    start = j
                    break
                else:
                    q += 1
                    j -= 1
            else:
                j -= 1
        else:
            start = 0

        # find the 3rd line after current comment
        finish = None
        j = pos
        q = 0
        while j != len(code):
            if code[j] == '\n':
                if q == 3:
                    finish = j
                    break
                else:
                    q += 1
                    j += 1
            else:
                j += 1
        else:
            finish = len(code)

        self.textEdit_before.insertPlainText(code[start:pos])
        
        self.textEdit_before.setTextColor(QtGui.QColor('red'))
        self.textEdit_before.insertPlainText(comment_list[i])
        
        self.textEdit_before.setTextColor(QtGui.QColor('black'))
        self.textEdit_before.insertPlainText(code[pos + len(comment_list[i]):finish])  

        if i < len(translated_comments):
            if translated_comments[i] is not None:
                self.textEdit_after.setText(translated_comments[i])
            else:
                self.textEdit_after.clear()
        else:
            self.textEdit_after.clear()
        
def main():
    app = QtGui.QApplication(sys.argv)
    form = MainForm()
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

# Global TODO:
# 1) Learn my tool how to make TODO-list
