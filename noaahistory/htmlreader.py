import os
import sys

__all__ = ['HTMLnode', 'HTMLreader']

class HTMLnode:	
    def __init__(self, tag, parent = None, content = ''):
        self.firstChild = None
        self.lastChild = None
        self.prevSib = None
        self.nextSib = None
        self.attr = {}
        self.tag = tag.strip().lower()
        self.content = content
        self.parent = parent

        if (parent != None):
            if (parent.firstChild == None):
                parent.firstChild = self
                parent.lastChild = self
            else:
                parent.lastChild.nextSib = self
                self.prevSib = parent.lastChild
                parent.lastChild = self

    def setAttr(self, key, value):
        t_key = key.strip()#.lower()
        t_value = value.strip()#.lower()
        if (len(t_key)>0 and len(t_value)>0):
            self.attr[t_key] = t_value

    def addContent(self, content):
        self.content += content

    def findElement(self, tag = None, key = None, value = None, depth=0):
        matches = []
        #print(self.tag, self.attr)
        if type(tag) != list:
            tag = [tag.strip().lower()]
        if (self.tag in tag or tag == None):
            if (key == None):
                matches.append(self)
            elif (key.strip().lower() in self.attr):
                if (self.attr[key] == value.strip() or value == None):
                    matches.append(self)
                    
        subTag = self.firstChild
        #print(self.tag, depth)

        while (subTag != None):
            matches += subTag.findElement(tag, key, value, depth+1)		
            subTag = subTag.nextSib
        
        return matches

    def printNode(self, fileOut = None):
        if fileOut == None:
            fout = sys.stdout
        else:
            fout = open(fileOut, 'w')

        self._printNode('', fout)
        fout.close()

    def _printNode(self, tabs = '', fileOut = sys.stdout):
        if self.tag != 'content':
            wstr = "<"+self.tag
            for k, v in self.attr.items():
                wstr += (" "+k+'=\"'+ v+'\"')
            fileOut.write(wstr + (">"))
        else:
            fileOut.write(self.content)
            return

        subTag = self.firstChild
        while (subTag != None):
            subTag._printNode(tabs+"\t", fileOut)
            subTag = subTag.nextSib

        fileOut.write("</"+self.tag+">")

    def getAllContent(self):
        if (self.tag == 'content'):
            return [self.content]
        else:
            build = []
        
        curNode = self.firstChild
        while (curNode != None):
            build += curNode.getAllContent()
            curNode = curNode.nextSib

        return build

    def __getitem__(self, key):
        if self.tag != 'table':
            raise RuntimeError('HTML <'+self.tag+'> tags are not subscriptable')
        
        rows = self.findElement('tr')[key[0]]
        out = []
        if (type(rows) == list):
            for r in range(len(rows)):
                columns = rows[r].findElement(['td'])
                try:
                    out.append(columns[key[1]])
                except:
                    pass
        else:
            columns = rows.findElement(['td'])
            out.append(columns[key[1]])
        
        for i in range(len(out)):
            if (type(out[i]) != list):
                out[i] = [out[i]]
            for j in range(len(out[i])):
                cont = out[i][j].getAllContent()
                if (len(cont) > 0):
                    cont = cont[0]
                else:
                    cont = ''
                out[i][j] = cont
        return out

INIT = 0
TAG = 1
TAG_NAME = 2
ATTR_KEY = 3
ATTR_VAL= 4
ATTR_VAL_QUOTE_ON = 5
ATTR_VAL_SQUOTE_ON = 6
ATTR_VAL_QUOTE_OFF = 7
SCRIPT = 8
SCRIPT_END = 9
CONTENT = 10
END_TAG = 11
COMMENT = 12
END_TAG_SCRIPT = 13
COMMENT_TAG = 14
COMMENT_PR = 15
STYLE_CSS = 16
END_TAG_STYLE =17
STYLE_END = 18

TAG_HIER = 0
TAG_VOID = 1
TAG_SCRIPT = 2
TAG_STYLE = 3

class HTMLreader:
    ## voidElements cannot have child tags
    voidElements = ["area", "base", "br", "col", "command", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr", "p"]
    states = ["INIT", "TAG", "TAG_NAME", "ATTR_KEY", "ATTR_VAL", "ATTR_VAL_QUOTE_ON", "ATTR_VAL_SQUOTE_ON", "ATTR_VAL_QUOTE_OFF", "SCRIPT", "SCRIPT_END", "CONTENT", "END_TAG", "COMMENT", "END_TAG_SCRIPT", "COMMENT_TAG", "COMMENT_PR", "STYLE_CSS", "END_TAG_STYLE", "STYLE_END"]

    def __init__(self, stream, printWarnings = False):
        self.state = INIT
        self.curBuild = ""
        self.AttrKey = ""
        self.AttrValue = ""
        self.scriptBuild = ""
        self.styleBuild = ""
        self.commentPrefix = False
        self.tagFlag = -1
        self.printWarnings = printWarnings
        self.curLine = 0
        
        self.head = None
        self.curNode = None

        data = stream.read()
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        for ch in data:
            self.parseHTML(ch)

    def printToFile(self, fpath = None):
        if fpath == None:
            fpath = os.path.dirname(__file__)+'/output.html'
        self.head.printNode(fileOut = fpath)

    def addNode(self, tag):
        self.curNode = HTMLnode(tag, self.curNode)
        if (self.head == None):
            self.head = self.curNode
    
    def upOneLevel(self):
        if (self.curNode != None):
            self.curNode = self.curNode.parent

    def addContent(self, content):
        self.addNode('content')
        self.curNode.addContent(content)
        self.upOneLevel()

    ##used to handle out of order end tags
    def returnToParent(self, tag):
        tempNode = self.curNode
        while (tempNode != None):
            if (tempNode.tag == tag.strip().lower()):
                if (tempNode.parent != None ):
                    self.curNode = tempNode.parent
                    return True
            tempNode = tempNode.parent
        return False
    
    def isTagVoid(self, tag):
        return tag.strip().lower() in self.voidElements

    def isTagTable(self, tag):
        return tag.strip().lower() in ['td', 'tr']
    
    def isTagScript(self, tag):
        return True if (tag.strip().lower() == "script") else False

    def isTagStyle(self, tag):
        return True if (tag.strip().lower() == "style") else False
    
    def stateTo(self, newState, tagFlag = None):
        self.state = newState
        if (tagFlag != None):
            self.tagFlag = tagFlag
        self.curBuild = ""
        #print(states[state]);
    
    def getHead(self):
        return self.head
    
    def findElement(self, tag = None, key = None, value = None):
        return self.head.findElement(tag, key, value)
    
    def parseHTML(self, ch):
        if self.state == INIT:
            if (ch == '<'): self.stateTo(TAG)

        elif self.state == TAG:
            if (ch == '/'): self.stateTo(END_TAG)
            elif (ch == '!'):
                self.stateTo(COMMENT_PR)
                self.curBuild += ch
            else:
                self.stateTo(TAG_NAME)
                self.curBuild += ch

        elif self.state == COMMENT_PR:
            if (ch == '-'): self.stateTo(COMMENT)
            else: self.stateTo(COMMENT_TAG)

        elif self.state == TAG_NAME:
            if ch.isspace():
                self.addNode(self.curBuild)
                if self.isTagVoid(self.curBuild): self.stateTo(ATTR_KEY, TAG_VOID)	
                elif (self.isTagScript(self.curBuild)):
                    self.stateTo(ATTR_KEY, TAG_SCRIPT)
                    self.scriptBuild = ""
                elif (self.isTagStyle(self.curBuild)):
                    self.stateTo(ATTR_KEY, TAG_STYLE)
                    self.styleBuild = ""
                else: self.stateTo(ATTR_KEY, TAG_HIER)

            elif (ch == '>'):
                if (self.isTagTable(self.curBuild)) and (self.curNode.tag == self.curBuild):
                    self.upOneLevel()
                if (self.curNode != None and self.curNode.tag == 'td' and self.curBuild == 'tr'):
                    self.upOneLevel()
                    self.upOneLevel()
                    
                self.addNode(self.curBuild)
                if (self.isTagVoid(self.curBuild)):
                    self.stateTo(CONTENT)
                    self.upOneLevel()
                elif (self.isTagScript(self.curBuild)):
                    self.stateTo(SCRIPT)
                    self.scriptBuild = ""
                elif (self.isTagStyle(self.curBuild)):
                    self.stateTo(STYLE_CSS)
                    self.styleBuild = ""
                else: self.stateTo(CONTENT)
            else: self.curBuild += ch

        elif self.state == ATTR_KEY:
            if (ch == '='):
                self.AttrKey = self.curBuild
                self.stateTo(ATTR_VAL)
            
            elif (ch == '>'):
                if (self.tagFlag == TAG_VOID):
                    self.upOneLevel()
                    self.stateTo(CONTENT); 
                elif (self.tagFlag == TAG_SCRIPT): self.stateTo(SCRIPT)
                elif (self.tagFlag == TAG_STYLE): self.stateTo(STYLE_CSS)
                elif (self.tagFlag == TAG_HIER): self.stateTo(CONTENT)
                else: print("TAG FLAG = "+self.tagFlag +".")
            else: self.curBuild += ch	

        elif self.state == ATTR_VAL:
            if (ch == '"'): self.stateTo(ATTR_VAL_QUOTE_ON)
            elif (ch == '\''):  self.stateTo(ATTR_VAL_SQUOTE_ON)
            elif (ch == '>'):
                if (self.tagFlag == TAG_VOID):
                    self.upOneLevel()
                    self.stateTo(CONTENT)
                elif (self.tagFlag == TAG_SCRIPT): self.stateTo(SCRIPT)
                elif (self.tagFlag == TAG_STYLE): self.stateTo(STYLE_CSS)
                elif (self.tagFlag == TAG_HIER): self.stateTo(CONTENT)
                else: print("TAG FLAG = "+self.tagFlag +".")

        elif self.state == ATTR_VAL_QUOTE_ON:
            if (ch == '"'):
                self.AttrValue = self.curBuild
                self.curNode.setAttr(self.AttrKey, self.AttrValue)
                self.stateTo(ATTR_VAL_QUOTE_OFF)
            else: self.curBuild += ch 

        elif self.state == ATTR_VAL_SQUOTE_ON:
            if (ch == '\''):
                self.AttrValue = self.curBuild
                self.curNode.setAttr(self.AttrKey, self.AttrValue)
                self.stateTo(ATTR_VAL_QUOTE_OFF)
            else: self.curBuild += ch

        elif self.state == ATTR_VAL_QUOTE_OFF:
            if (ch.isspace()): self.stateTo(ATTR_KEY)
            elif (ch == '>'):
                if (self.tagFlag == TAG_VOID):
                    self.upOneLevel()
                    self.stateTo(CONTENT)
                elif (self.tagFlag == TAG_SCRIPT): self.stateTo(SCRIPT)
                elif (self.tagFlag == TAG_STYLE): self.stateTo(STYLE_CSS)
                elif (self.tagFlag == TAG_HIER): self.stateTo(CONTENT)
                else: print("TAG FLAG = "+self.tagFlag +".")		

        elif self.state == CONTENT:
            if (ch == '<'):
                self.addContent(self.curBuild)
                self.stateTo(TAG)
            else: self.curBuild += ch

        elif self.state == SCRIPT_END:
            if (ch == '/'):
                self.stateTo(END_TAG_SCRIPT)
            else:
                self.stateTo(SCRIPT)
                self.scriptBuild += ("<"+ch)

        elif self.state == END_TAG_SCRIPT:
            if (ch == '>'):
                if (self.curBuild.strip().lower() == 'script'):
                    self.addContent(self.scriptBuild)
                    self.upOneLevel()
                    self.stateTo(CONTENT)
                else:
                    self.stateTo(SCRIPT)
                    self.scriptBuild += ("</"+self.curBuild+ch)
            elif (ch.isspace()):
                self.stateTo(SCRIPT)
                self.scriptBuild += ("</"+self.curBuild+ch)
            elif (ch == '<'):
                self.stateTo(SCRIPT_END)
                self.scriptBuild += ("</"+self.curBuild+ch)
            else: self.curBuild += ch

        elif self.state == STYLE_END:
            if (ch == '/'):
                self.stateTo(END_TAG_STYLE)
            else:
                self.stateTo(STYLE_CSS)
                self.styleBuild += ("<"+ch)

        elif self.state == END_TAG_STYLE:
            if (ch == '>'):
                if (self.curBuild.strip().lower() == 'style'):
                    self.addContent(self.styleBuild)
                    self.upOneLevel()
                    self.stateTo(CONTENT)
                else:
                    self.stateTo(STYLE)
                    self.scriptBuild += ("</"+self.curBuild+ch)
            elif (ch.isspace()):
                self.stateTo(STYLE)
                self.styleBuild += ("</"+self.curBuild+ch)
            elif (ch == '<'):
                self.stateTo(STYLE_END)
                self.styleBuild += ("</"+self.curBuild+ch)
            else: self.curBuild += ch

        elif self.state == END_TAG:
            if (ch == '>'):
                if(self.isTagVoid(self.curBuild)):
                    self.stateTo(CONTENT); 
                elif (self.curBuild.strip().lower() == self.curNode.tag):
                    self.upOneLevel()
                    self.stateTo(CONTENT)
                elif self.returnToParent(self.curBuild):
                    ##print warning
                    self.stateTo(CONTENT)
                else:
                    if (self.printWarnings): print("WARNING on line "+self.curLine+": </"+self.curBuild.strip()+"> is misplaced. Current tag: <"+self.curNode.tag+">.")
                    self.stateTo(CONTENT)
            else: self.curBuild += ch

        elif self.state == SCRIPT:
            if (ch == '<'):
                self.stateTo(SCRIPT_END)
            else:
                self.scriptBuild += ch

        elif self.state == STYLE_CSS:
            if (ch == '<'):
                self.stateTo(STYLE_END)
            else:
                self.styleBuild += ch

        elif self.state == COMMENT:
            if (ch == '-'):
                self.commentPrefix = True
            elif ((ch == '>') and (self.commentPrefix)):
                self.stateTo(CONTENT)
                self.commentPrefix = False
            else:
                self.commentPrefix = False
        elif self.state == COMMENT_TAG:
            if (ch == '>'):
                if (self.curNode == None):
                    self.stateTo(INIT)
                else:
                    self.stateTo(CONTENT)

        else:
            if (self.printWarnings): print("Invalid State: "+self.state+".\n")

