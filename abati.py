# Synidaemi: (reyndar ekki graena svarid)
# http://stackoverflow.com/questions/523363/how-do-i-layout-a-3-pane-window-using-wxpython
#
# Notkun a AUI frameworkinu:
# http://xoomer.virgilio.it/infinity77/wxPython/aui/wx.aui.AuiPaneInfo.html
#112

import wx
import wx.aui
import wx.lib.scrolledpanel as scrolled
import splitsymbols
import wx.lib.agw.hyperlink as hl
import rss_get_news
import buyorsell

# matplotlib---------------
import matplotlib
matplotlib.use('WXAgg')

from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from matplotlib.dates import AutoDateLocator
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.ticker import MaxNLocator
# matplotlib---------------    

# abati-----------------
import ystockquote
import movAVG
import numpy
import bollinger
from pylab import * 
from datetime import time,datetime,date, timedelta
import matplotlib.pyplot as plt
import sys
# abati-----------------



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, size=(1000,700), *args, **kwargs)
        
        self.currentsymbol = ''
        self.changestr = ''
        self.changeperc = ''
        self.companyname = 'Press \'Plot Data\' to update'
        self.timabil = 200
        self.delta = 20


        self.mgr = wx.aui.AuiManager(self)
        
        self.leftpanel = wx.Panel(self,-1,size = (100,150))
        self.rightpanel = wx.Panel(self, -1, size = (200, 150))
        self.toppanel = wx.Panel(self, -1, size = (200, 100))
        self.topleftpanel = wx.Panel(self, -1, size = (200, 100))
        self.buypanel = wx.Panel(self, -1, size = (200, 100))
        self.newspanel = wx.Panel(self, -1, size = (200, 30))

        
        self.btn1 = wx.Button(self.toppanel, label='Plot Data')
        self.Bind(wx.EVT_BUTTON, self.GetData, self.btn1)
        
        
        self.periodText = wx.StaticText(self.toppanel, -1, "Viewing period:")
        self.period = wx.TextCtrl(self.toppanel, -1, "", size=(75, -1))
        

        self.avgText = wx.StaticText(self.toppanel, -1, "Moving average period:")
        self.avg = wx.TextCtrl(self.toppanel, -1, "", size=(75, -1))
        self.inputsizer = wx.FlexGridSizer(cols=3, hgap=6, vgap=6)

        self.days1 = wx.StaticText(self.toppanel, -1, "days")
        self.days2 = wx.StaticText(self.toppanel, -1, "days")

        self.lamefix = wx.StaticText(self.toppanel, -1, "")
        self.inputsizer.AddMany([self.periodText, self.period, self.days1,self.avgText, self.avg,self.days2,self.lamefix,self.btn1])
        
        #Text box which displays main info about selected symbol
        self.maintext = wx.StaticText(self.topleftpanel,size=(350,25))
        self.maintext.SetFont(wx.Font(18, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        
        self.hbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox.Add(self.maintext)
        self.hbox.Add(self.inputsizer)
        
        self.toppanel.SetSizer(self.hbox)
        

        
        menubar = wx.MenuBar()
        menufile = wx.Menu()
        menuhelp = wx.Menu()
        

        quit = wx.MenuItem(menufile, 115, '&Quit\tCtrl+Q', 'Quit the Application')
        self.Bind(wx.EVT_MENU, self.OnClose, quit)
        menufile.AppendItem(quit)


        getandplot = wx.MenuItem(menufile, 105, '&Plot\tCtrl+P', 'Plot data')
        self.Bind(wx.EVT_MENU, self.GetData, getandplot)
        menufile.AppendItem(getandplot)

        
        about = wx.MenuItem(menufile,137,'&About','About this application')
        self.Bind(wx.EVT_MENU,self.OnAbout,about)
        menuhelp.AppendItem(about)
        
        menubar.Append(menufile, '&File')
        menubar.Append(menuhelp, '&Help')


        
        self.SetMenuBar(menubar)
        
        #Biglist : list of lists of each symbol + corporation name
        #symbolist : list of all nasdaq symbols
        self.biglist = splitsymbols.readsymbols('nasdaqlist.txt')
        symbolist = []
        
        for i in range(1,len(self.biglist)-1):
            symbol = self.biglist[i][0]
            symbolist.append(symbol)
        
        self.slist = wx.ListBox(self.leftpanel,42, wx.DefaultPosition, (100,100), symbolist)
        self.Bind(wx.EVT_LISTBOX, self.OnSymbolSelect,id=42)
        
        
        
        #Image canvas for historical plot of selected symbol
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.fig.subplots_adjust(bottom=0.15)
        self.fig.suptitle("Please select a ticker\n on from the list on the left\n Press \'Plot Data\' for graph", fontsize=20)

        self.canvas = FigCanvas(self.rightpanel,-1,self.fig)

        #One rows, two columns
        self.gs = gridspec.GridSpec(2, 1, height_ratios=[3,1.5])

        
        # Newsfeed things
        self.newsbtn1 = wx.Button(self.newspanel, label='Next', pos=(90, 3))
        self.newsbtn2 = wx.Button(self.newspanel, label='Previous', pos=(0, 3))
        self.Bind(wx.EVT_BUTTON, self.SwitchNewsNext, self.newsbtn1)
        self.Bind(wx.EVT_BUTTON, self.SwitchNewsPrevious, self.newsbtn2)
        self.newsnumber = wx.StaticText(self.newspanel,size=(350,20), pos=(190, 4))
        self.newsnumber.SetFont(wx.Font(16, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.newsnumber.SetLabel("1/20")
        self.newstitle = wx.StaticText(self.newspanel,size=(350,20), pos=(360, 4))
        self.newstitle.SetFont(wx.Font(16, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        
        
        self.newstoshow = 0
        try:
            self.newsholder = rss_get_news.pull_titles_and_links(rss_get_news.fetch("goog"))
            self.newstitle.SetLabel(self.newsholder[0][self.newstoshow])
        except:
            self.NoInternetConnection()
            self.newsholder = "no internet connection"
        self.hyper1 = hl.HyperLinkCtrl(self.newspanel, -1, "Click here to read.", pos=(245, 7), URL=self.newsholder[1][self.newstoshow])


        
        # *** Sizer for rightpanel ***
        self.sizer_for_rightpanel = wx.BoxSizer(wx.VERTICAL) # sizer_for_rightpanel is a new sizer
        self.sizer_for_rightpanel.Add(self.canvas, 1, wx.GROW) # add things that are in the rightpanel to the sizer with wanted attribute (here: wx.GROW)
        self.rightpanel.SetSizer(self.sizer_for_rightpanel) # set the sizer as default sizer for rightpanel
        # *** Sizer for rightpanel ***
        
        # *** Sizer for leftpanel ***
        self.sizer_for_leftpanel = wx.BoxSizer(wx.VERTICAL) # sizer_for_leftpanel is a new sizer
        self.sizer_for_leftpanel.Add(self.slist, 1, wx.GROW) # add things that are in the leftpanel to the sizer with wanted attribute (here: wx.GROW)
        self.leftpanel.SetSizer(self.sizer_for_leftpanel) # set the sizer as default sizer for leftpanel
        # *** Sizer for leftpanel ***
        
        self.mgr.AddPane(self.leftpanel, wx.aui.AuiPaneInfo().Left().CloseButton(False).Caption("Corporation tickers"))
        self.mgr.AddPane(self.rightpanel, wx.aui.AuiPaneInfo().Center().Layer(1).CloseButton(False).Caption("rightpanel").CaptionVisible(False))
        self.mgr.AddPane(self.buypanel, wx.aui.AuiPaneInfo().Top().Layer(1).CloseButton(False).Caption("Buy or Sell"))
        self.mgr.AddPane(self.toppanel, wx.aui.AuiPaneInfo().Top().Layer(1).CloseButton(False).Caption("Plot controls"))
        self.mgr.AddPane(self.topleftpanel, wx.aui.AuiPaneInfo().Top().Layer(1).CloseButton(False).Caption("Corporation name"))
        self.mgr.AddPane(self.newspanel, wx.aui.AuiPaneInfo().Bottom().Layer(3).CloseButton(False).Caption("News"))
        
        #Buy/Sell Panel
        self.buytxt =  wx.StaticText(self.buypanel, 46, "Stocks for \n"+ self.companyname)
        self.buytxt.SetFont(wx.Font(18, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.buyorsell = wx.TextCtrl(self.buypanel, 46,  "SELL or BUY?", size=(300, -1)) 
        self.buyorsell.SetFont(wx.Font(18, wx.ROMAN, wx.NORMAL, wx.NORMAL)) 

        self.buysizer = wx.FlexGridSizer(cols=2, hgap=1, vgap=6) 
        self.buysizer.AddMany([self.buytxt,self.buyorsell])
        self.buypanel.SetSizer(self.buysizer)
        #Buy/Sell Panel

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.buytxt)
        self.vbox.Add(self.buyorsell)
        self.buypanel.SetSizer(self.vbox)
        
        self.mgr.Update()

    def NoInternetConnection(self):
        dlg = wx.MessageDialog(self,
           "Cannot retrieve data from servers, check your internet connection",
           "No Internet Connection", wx.OK|wx.ICON_ERROR)
        result = dlg.ShowModal()
        dlg.Destroy()

    def SelectTicker(self):
        dlg = wx.MessageDialog(self,
           "Please select a ticker from the list on the left",
           "", wx.OK|wx.ICON_INFORMATION)
        result = dlg.ShowModal()
        dlg.Destroy()
        
    
    def UpdateNewsPanel(self):
        self.newstitle.SetLabel(self.newsholder[0][self.newstoshow])
        self.newsnumber.SetLabel("{0}/{1}".format((self.newstoshow+1),len(self.newsholder[0])))
        self.hyper1.SetURL(self.newsholder[1][self.newstoshow]) 
        self.hyper1.UpdateLink(True)
    
    def SwitchNewsNext(self,event):
        self.newstoshow = self.newstoshow + 1
        if not self.newstoshow < len(self.newsholder[0]):
            self.newstoshow = self.newstoshow - len(self.newsholder[0])
        self.UpdateNewsPanel()
    
    def SwitchNewsPrevious(self,event):
        self.newstoshow = self.newstoshow - 1
        if self.newstoshow < 0:
            self.newstoshow = self.newstoshow + len(self.newsholder[0])
        self.UpdateNewsPanel()
    
    def SetPeriod(self,event):
        self.timabil = self.pslider.GetValue()
        print self.timabil
        

    def OnClose(self, event):
       dlg = wx.MessageDialog(self,
           "Do you really want to close this application?",
           "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
       result = dlg.ShowModal()
       dlg.Destroy()
       if result == wx.ID_OK:
           self.Destroy()

    def OnAbout(self,event):
        bout = wx.MessageDialog(self,"Authors: \nGunnar Orn Gunnarsson \nGudmundur Mar Gunnarsson \nSveinn Floki Gudmundsson \nTomas Pall Mate","About",wx.OK)
        result2 = bout.ShowModal()
        if result2 == wx.ID_OK:
            bout.Destroy()
    #Gets the selected symbol (as string) from the ListBox
    def OnSymbolSelect(self,event):
        self.currentsymbol = event.GetString()
        self.currentvalue = event.GetSelection()
        
        try:
            # update newspanel
            self.newsholder = rss_get_news.pull_titles_and_links(rss_get_news.fetch(self.currentsymbol))

            self.newstoshow = 0
            self.UpdateNewsPanel()
        #update newspanel
        except:
            self.NoInternetConnection()
            return
        
        #Quick Info
        now = date.today()
        dagsetn_nuna = now.strftime("%Y%m%d")
        then = date.today() - timedelta(5)
        dagsetn_tha = then.strftime("%Y%m%d")
        
        try:
            self.lastpricelist = ystockquote.get_historical_prices(self.currentsymbol, dagsetn_tha, dagsetn_nuna)
        except:
            if self.currentsymbol=="":
             self.SelectTicker()
            else:
             self.NoInternetConnection()
            return
        
        lastprice = float(self.lastpricelist[1][6])
        #print(self.lastpricelist)
        

        self.currentprice = float(ystockquote.get_price(self.currentsymbol))
        
        change = self.currentprice-lastprice
        change = round(change,2)
        
        if change < 0:
            self.changestr = str(change)
            self.changeperc = str(round((change/lastprice)*100,2))+'%'
        else:
            self.changestr = '+'+str(change)
            self.changeperc = '('+str(round((change/lastprice)*100,2))+'%'+')'
        
        #Writes ticker and name of company
        self.companyname = self.biglist[self.currentvalue+1][1].split('-')[0]
        self.maintext.SetLabel(self.companyname)
        
        #Deletes previous stockpricetext object ( no clear option, has to be rebuilt )
        try:
         self.stockpricetext.Destroy()
        except:
         pass
        
        self.stockpricetext = wx.StaticText(self.topleftpanel, pos=(0,40),size=(100,20),style=wx.TE_READONLY)
        self.stockpricetext.SetFont(wx.Font(16, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.stockpricetext.SetLabel(' ')
        
        
        if float(self.changestr) > 0:
            #self.stockpricetext.SetLabel(' ')
            self.stockpricetext.SetForegroundColour((0,200,0)) # set text color
        elif float(self.changestr) < 0:
            #self.stockpricetext.SetLabel(' ')
            self.stockpricetext.SetForegroundColour((200,0,0)) # set text color
        self.stockpricetext.SetLabel(str(self.currentprice)+'  '+ self.changestr + '  '+self.changeperc)


    def GetData(self,event):
        
        try:
            self.timabil = int(self.period.GetValue())
        except:
            self.period.SetValue("200")
        try:
            self.delta = int(self.avg.GetValue())
        except:
            self.avg.SetValue("20")
    
        if self.currentsymbol=='':
            self.SelectTicker()
        else:

         
            # **** to remove title text in matplotlib graph ****
            self.fig.clear()
            self.axes = self.fig.add_subplot(self.gs[0],axisbg='black')
            self.axes1 = self.fig.add_subplot(self.gs[1],axisbg='black')
            
            #Name of company
            self.companyname = self.biglist[self.currentvalue+1][1].split('-')[0]
            self.fig.suptitle(self.companyname, fontsize=20)
            
            
            
            self.sizer_for_rightpanel = wx.BoxSizer(wx.VERTICAL)
            self.sizer_for_rightpanel.Add(self.canvas, 1, wx.GROW)
            self.rightpanel.SetSizer(self.sizer_for_rightpanel)
            self.mgr.Update()
            # **** to remove title text in matplotlib graph ****
            
            
            now = date.today()
            dagsetn_nuna = now.strftime("%Y%m%d")
            
            #dagsetning fyrir 'timabil' dogum
            then = date.today() - timedelta(self.delta+self.timabil+1) #+1 thvi fyrsti dalkur i datalist er heiti dalka 
            then2 = date.today() - timedelta(self.timabil+1)
            dagsetn_tha = then.strftime("%Y%m%d")
            try:    
                datalist = ystockquote.get_historical_prices(self.currentsymbol, dagsetn_tha, dagsetn_nuna)
            except:
                self.NoInternetConnection()
                return
        
            dates = []
            viewdata = []

            
            # datalist: list of values for open days in the selected period of days + delta days
            # back in time (to calculate moving average for the first day) 
            for i in range(1,len(datalist)):
                date1 = datetime.strptime(datalist[i][0],"%Y-%m-%d")
                self.place = i
                if date1.date() <= then2:
                    viewdata = datalist[1:i+1] 
                    #+1 because the list is backwards. 
                    #(value for today is first in the list)
                    break
        
            for i in range(len(viewdata)):
                date2 = datetime.strptime(viewdata[i][0],"%Y-%m-%d")
                dates.append(date2)
                
            dates.reverse()
            dates = matplotlib.dates.date2num(dates)
            
            volume = []
            price = []
            openprice = []
            closeprice = []


            
            
            for x in datalist[1:]:
                openprice.append(float(x[1]))
                closeprice.append(float(x[4]))
                price.append(float(x[6]))
                volume.append(float(x[5]))
            

            color = []
            for i in range(len(openprice)):
                if openprice[i]<closeprice[i]:
                    color.append('r')
                elif openprice[i] > closeprice[i]:
                    color.append('g')
                else: color.append('grey')
            (pricemean,pricestd) = movAVG.AVG(price,self.place,self.delta)
            
            
            (priceupperb,pricelowerb,lastUpInner,lastLoInner) = bollinger.bollinger(pricemean,pricestd,self.delta)

            #Take the last values for the bollinger bands, moving average and the current price
            #To find out whether there's a bollinger squeeze or you can 

            #BuyOrSellCheck
            bos =  buyorsell.BuyOrSell(self.currentprice ,openprice[0] ,lastUpInner, lastLoInner)
            
            if bos == "NEUTRAL":
                self.buytxt.SetLabel("Stocks for \n" + self.companyname)
                self.buyorsell.SetValue("are in a NEUTRAL zone")
            elif bos == "BUY":
                self.buytxt.SetLabel("Stocks for \n"+self.companyname)
                self.buyorsell.SetValue("are in the BUY zone")
            elif bos == "SELL":
                self.buytxt.SetLabel("Stocks for \n"+self.companyname)
                self.buyorsell.SetValue("are in the SELL zone")    
            



            volume.reverse()
            price.reverse()
            pricemean.reverse()
            
            priceupperb.reverse()
            pricelowerb.reverse()
            
            self.axes.clear()

            self.axes1.clear()
            
            #self.axes.xaxis.set_major_locator(MultipleLocator((int)(len(price[volume])/10))
            self.axes.plot_date(dates,price[:self.place],color='yellow',linewidth='1',linestyle='-',marker='None',ydate=False)
            self.axes.plot_date(dates,pricemean[:self.place], color='red',linestyle='-',marker='None',ydate=False)
            self.axes.plot_date(dates,priceupperb,color='green',linestyle='-',marker='None',ydate=False)
            self.axes.plot_date(dates,pricelowerb,color='green',linestyle='-',marker='None',ydate=False)
            
            
            
            plt.setp( self.axes.xaxis.get_majorticklabels(),visible=False )
            self.axes.set_ylabel('Price (per share)')
            self.axes.yaxis.grid(color='gray', linestyle='dashed')
            self.axes.xaxis.grid(color='gray', linestyle='dashed')


            
            
            #self.axes1.xaxis.set_major_locator(MultipleLocator(int(len(volume)/10))
            plt.setp( self.axes1.xaxis.get_majorticklabels(),horizontalalignment='right', rotation=25 )        
            plt.setp( self.axes1.yaxis.get_majorticklabels(),fontsize=9 )
            self.axes1.xaxis_date()

            #self.axes1.xaxis.set_major_formatter( DateFormatter('%d:%m:%Y'))
            #when the bars will mash together if they're shown for a bigger period than 150
            if self.timabil < 151:
             self.axes1.bar(dates,volume[:self.place], color=color, align='center')
            #shows a line graph instead of a bar chart if over 150 day timeperiod is selected
            else:
             self.axes1.plot_date(dates, volume[:self.place], ydate=False, marker='',color='yellow', linestyle='-',  linewidth=0.5)
            self.axes1.set_ylabel('Volume')
            self.axes1.yaxis.grid(color='gray', linestyle='dashed', alpha=0.5)
            self.axes1.xaxis.grid(color='gray', linestyle='dashed', alpha=0.5)
            
            
            self.axes.fill_between(dates,priceupperb,pricelowerb,facecolor='green',alpha=0.3)


            DateLoc = AutoDateLocator(maxticks=12)

            self.axes.xaxis.set_major_locator(DateLoc)
            self.axes1.xaxis.set_major_locator(DateLoc)
            self.axes1.xaxis.set_major_formatter( DateFormatter('%d %b %Y'))
            self.fig.autofmt_xdate()
            # if ( DateFormatter.scale == 365.0 ):
            #     self._formatter = DateFormatter("%Y", self._tz)
            # elif ( scale == 30.0 ):
            #     self._formatter = DateFormatter("%b %Y", self._tz)
            # elif ( (scale == 1.0) or (scale == 7.0) ):
            #     self._formatter = DateFormatter("%b %d \n %Y", self._tz)
            
            
            self.canvas.draw()
       



class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'Hopur9')
        frame.Show()
        self.SetTopWindow(frame)
        return 1

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()