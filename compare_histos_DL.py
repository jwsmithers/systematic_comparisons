from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText,TLegend, TF1, TLatex
from ROOT import gROOT,TGaxis
gROOT.SetBatch(True)
import sys
import os

from difflib import SequenceMatcher
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

ee_path="/afs/cern.ch/work/j/jwsmith/ttgammaPlottingPipeline/build/ee_fullFit_merged_C_On/build/SR1_ttgamma_SR1_ee_2018_03/ttgamma_SR1_ee_2018_03/Histograms/"
ee_root_file="ttgamma_SR1_ee_2018_03_event_ELD_MVA_ee_histos.root"
mumu_path="/afs/cern.ch/work/j/jwsmith/ttgammaPlottingPipeline/build/mumu_fullFit_merged_C_On/build/SR1_ttgamma_SR1_mumu_2018_03/ttgamma_SR1_mumu_2018_03/Histograms/"
mumu_root_file="ttgamma_SR1_mumu_2018_03_event_ELD_MVA_mumu_histos.root"
emu_path="/afs/cern.ch/work/j/jwsmith/ttgammaPlottingPipeline/build/emu_fullFit_merged_C_On/build/SR1_ttgamma_SR1_emu_2018_03/ttgamma_SR1_emu_2018_03/Histograms/"
emu_root_file="ttgamma_SR1_emu_2018_03_event_ELD_MVA_emu_histos.root"

dilepton_path="/afs/cern.ch/work/j/jwsmith/ttgammaPlottingPipeline/build/dilepton_fullFit_merged_C_On/build/SR1_ee_mumu_emu_merged/ee_mumu_emu_merged/Histograms/"
dilepton_root_file="ee_mumu_emu_merged_event_ELD_MVA_ee_histos.root"

channels=["dilepton","ee","mumu","emu"]

g=globals()
for i in channels:
  g[i+"_nominal"] = []
  g[i+"_up"] = []
  g[i+"_down"] = []

def create_lists(channel,path,process):
  histograms=[]
  f = TFile.Open(path, 'read')
  dirlist = f.GetListOfKeys()
  iter = dirlist.MakeIterator()
  key = iter.Next()
  td = None
  while key:
    if key.GetClassName() == 'TH1F':
      td = key.ReadObj()
      hName = td.GetName()
      histograms.append(hName)
    key = iter.Next()

  for i in histograms:
    if "Data" in i: 
      continue
    prefixes=["event_ELD_MVA_ee_"+process,"event_ELD_MVA_mumu_"+process,"event_ELD_MVA_emu_"+process]
    if any(proc in i for proc in prefixes):
      i_split = i.split("_")
      if i_split[-1]==process:
        g[channel+"_nominal"].append(i)
      elif i_split[-1]=="Up":
        g[channel+"_up"].append(i)
      elif i_split[-1]=="Down":
        g[channel+"_down"].append(i)

  f.Close()

def make_ratio(nom,up,down,channel):
  ratio1 = up.Clone("ratio")
  #ratio1.Sumw2()
  ratio1.SetStats(0)
  ratio1.Add(nom,-1)
  ratio1.Divide(nom)
  ratio1.Scale(100)
  ratio1.SetTitle("")
  y = ratio1.GetYaxis()
  y.SetTitle("#frac{Syst-Nom.}{Nom.} [%]")
  y.SetNdivisions(505)
  y.SetTitleOffset(2.3)
  y.SetTitleSize(10)
  x = ratio1.GetXaxis()
  x.SetTitle("event level descriminator")
  x.SetTitleOffset(6.2)
  ratio1.SetLineColor(632)
  ratio1.SetFillColor(632)
  ratio1.SetMarkerColor(632)
  ratio1.SetMarkerStyle(0)
  ratio2 = down.Clone("ratio")
  #ratio2.Sumw2()
  ratio2.Add(nom,-1)
  ratio2.Divide(nom)
  ratio2.Scale(100)
  ratio2.SetLineColor(857)
  ratio2.SetFillColor(857)
  ratio2.SetMarkerColor(857)
  ratio2.SetMarkerStyle(0)
  line = TF1("fa1","0",-1000,1000);
  line.SetLineColor(1);
  ymax = abs(ratio1.GetMaximum());
  ymin = abs(ratio2.GetMaximum());
  Range=[ymax,ymin]
  maxv=max(Range)
  if maxv<0.8:
    offset=0.2
  else:
    offset=0.8
  ratio1.SetMinimum(-maxv-offset)
  ratio1.SetMaximum(maxv+offset)
  ratio2.SetMinimum(-maxv-offset)
  ratio2.SetMaximum(maxv+offset)

  ratio1.Draw("hist")
  ratio2.Draw("same hist")
  line.Draw("same")

  #axis1 = TGaxis(0,-maxv-offset,1,-maxv-offset,-maxv-offset,-maxv-offset,50510,"-");
  #axis1.SetName("axis1");

  channel_label = TLatex();
  channel_label.SetNDC();
  channel_label.SetTextAlign(12);
  channel_label.SetTextFont(63);
  channel_label.SetTextSizePixels(15);
  channel_label.DrawLatex(0.45,0.89, channel);
  channel_label.Draw("same")

  return ratio1, ratio2, line, channel_label

def plot_histos(process):
  for hist_int in range(0,len(ee_up)):
    f_ee = TFile.Open(ee_path+ee_root_file, 'read')
    f_mumu = TFile.Open(mumu_path+mumu_root_file, 'read')
    f_emu = TFile.Open(emu_path+emu_root_file, 'read')
    f_DL = TFile.Open(dilepton_path+dilepton_root_file, 'read')
    c1 = TCanvas( 'c1', 'Histogram Drawing Options', 0,0,800,800 )
    pad1 = TPad("pad1", "pad1", 0, 0.43, 1, 1.0)
    pad1.SetBottomMargin(0)  # joins upper and lower plot
    pad1.Draw()
    pad2 = TPad("pad2", "pad2", 0, 0.36, 1, 0.43)
    pad2.SetTopMargin(0.0)  # joins upper and lower plot
    pad2.SetBottomMargin(0)
    pad2.Draw()
    pad3 = TPad("pad3", "pad3", 0, 0.29, 1, 0.36)
    pad3.SetTopMargin(0.0)  # joins upper and lower plot
    pad3.SetBottomMargin(0)
    pad3.Draw()
    pad4 = TPad("pad4", "pad4", 0, 0.22, 1, 0.29)
    pad4.SetTopMargin(0.0)  # joins upper and lower plot
    pad4.SetBottomMargin(0)
    pad4.Draw()
    pad5 = TPad("pad5", "pad5", 0, 0.05, 1, 0.22)
    pad5.SetTopMargin(0.0)  # joins upper and lower plot
    pad5.SetBottomMargin(0.4)
    pad5.Draw()

    pad1.cd()
  
    hist_name_ee=ee_up[hist_int]
    hist_name_mumu=mumu_up[hist_int]
    hist_name_emu=emu_up[hist_int]
    hist_name_dilepton=dilepton_up[hist_int]
  
    sim1 = similar(hist_name_ee,hist_name_mumu)
    sim2 = similar(hist_name_mumu,hist_name_emu)
    if "ttphoton_PDF" not in hist_name_ee:
      if sim1 < 0.9 or sim2 < 0.9:
        print hist_name_ee," and ", hist_name_mumu, " are different!"
        sys.exit()
      sim3 = similar(hist_name_dilepton,hist_name_ee)
      # These should be identical
      if sim3 != 1.0:
        print hist_name_dilepton," and ", hist_name_ee, " are different!"
        sys.exit()

    g["nom_h_ee"] = f_ee.Get(ee_nominal[0])
    g["up_h_ee"] = f_ee.Get(ee_up[hist_int])
    g["down_h_ee"] = f_ee.Get(ee_down[hist_int])
    g["nom_h_mumu"] = f_mumu.Get(mumu_nominal[0])
    g["up_h_mumu"] = f_mumu.Get(mumu_up[hist_int])
    g["down_h_mumu"] = f_mumu.Get(mumu_down[hist_int])
    g["nom_h_emu"] = f_emu.Get(emu_nominal[0])
    g["up_h_emu"] = f_emu.Get(emu_up[hist_int])
    g["down_h_emu"] = f_emu.Get(emu_down[hist_int])

    g["nom_h_dilepton"] = f_DL.Get(dilepton_nominal[0])
    g["up_h_dilepton"] = f_DL.Get(dilepton_up[hist_int])
    g["down_h_dilepton"] = f_DL.Get(dilepton_down[hist_int])
  
  
    for i in channels:
      y1 = g["up_h_"+i].GetYaxis()
      y1.SetTitle("Events")
      y1.SetTitleOffset(2)
      x1 = g["up_h_"+i].GetXaxis()
      x1.SetTitle("event level descriminator")
      g["up_h_"+i].SetTitle("")
      x1.SetTitleOffset(1.5)
      g["up_h_"+i].Draw("same")
      g["down_h_"+i].Draw("same")
      g["nom_h_"+i].Draw("same")
  
    nom_h_ee.SetMarkerColor(1)
    nom_h_ee.SetLineColor(1)
    up_h_ee.SetMarkerColor(632)
    up_h_ee.SetLineColor(632)
    down_h_ee.SetMarkerColor(857)
    down_h_ee.SetLineColor(857)
  
    nom_h_mumu.SetMarkerStyle(4)
    nom_h_mumu.SetMarkerColor(1)
    nom_h_mumu.SetLineColor(1)
    up_h_mumu.SetMarkerColor(632)
    up_h_mumu.SetLineColor(632)
    up_h_mumu.SetMarkerStyle(4)
    down_h_mumu.SetMarkerColor(857)
    down_h_mumu.SetLineColor(857)
    down_h_mumu.SetMarkerStyle(4)

    nom_h_emu.SetMarkerStyle(4)
    nom_h_emu.SetMarkerColor(1)
    nom_h_emu.SetLineColor(1)
    up_h_emu.SetMarkerColor(632)
    up_h_emu.SetLineColor(632)
    up_h_emu.SetMarkerStyle(4)
    down_h_emu.SetMarkerColor(857)
    down_h_emu.SetLineColor(857)
    down_h_emu.SetMarkerStyle(4)
  
    nom_h_dilepton.SetMarkerStyle(26)
    nom_h_dilepton.SetMarkerColor(1)
    nom_h_dilepton.SetLineColor(1)
    up_h_dilepton.SetMarkerColor(632)
    up_h_dilepton.SetLineColor(632)
    up_h_dilepton.SetMarkerStyle(26)
    down_h_dilepton.SetMarkerColor(857)
    down_h_dilepton.SetLineColor(857)
    down_h_dilepton.SetMarkerStyle(26)
  
    legend = TLegend(0.15,0.4,0.55,0.85);
  
    for i in channels:
      if i=="dilepton":
        legend.AddEntry(g["nom_h_"+i],g[i+"_nominal"][0].replace("event_ELD_MVA_","").replace("ee","SL").replace("_regBin","")+" nominal","lep");
        legend.AddEntry(g["up_h_"+i],g[i+"_up"][hist_int].replace("event_ELD_MVA_","").replace("ee","SL").replace("_regBin",""),"lep");
        legend.AddEntry(g["down_h_"+i],g[i+"_down"][hist_int].replace("event_ELD_MVA_","").replace("ee","SL").replace("_regBin",""),"lep");
      else:
        legend.AddEntry(g["nom_h_"+i],g[i+"_nominal"][0].replace("event_ELD_MVA_","").replace("_regBin","")+" nominal","lep");
        legend.AddEntry(g["up_h_"+i],g[i+"_up"][hist_int].replace("event_ELD_MVA_","").replace("_regBin",""),"lep");
        legend.AddEntry(g["down_h_"+i],g[i+"_down"][hist_int].replace("event_ELD_MVA_","").replace("_regBin",""),"lep");
  
  
    legend.SetBorderSize(0)
    legend.SetTextSize(0.03)
    legend.SetFillColorAlpha(1,0)
    legend.Draw();
  
    c1.Update()
  
    pad2.cd()
    r1=make_ratio(nom_h_ee,up_h_ee,down_h_ee,"ee")
    pad3.cd()
    r2=make_ratio(nom_h_mumu,up_h_mumu,down_h_mumu,"#mu#mu")
    pad4.cd()
    r4=make_ratio(nom_h_emu,up_h_emu,down_h_emu,"e#mu")
    pad5.cd()
    r5=make_ratio(nom_h_dilepton,up_h_dilepton,down_h_dilepton,"dilepton")

 

    if not os.path.exists("histos/"+process+"/"):
        os.makedirs("histos/"+process+"/")
  
    c1.SaveAs("histos/"+process+"/"+hist_name_ee+".pdf")
    del c1
    for i in channels:
      del g["nom_h_"+i]
      del g["up_h_"+i]
      del g["down_h_"+i]
    

def main(Process):
  create_lists("ee", ee_path+ee_root_file,Process)
  create_lists("mumu",mumu_path+mumu_root_file,Process)
  create_lists("emu",emu_path+emu_root_file,Process)
  create_lists("dilepton",dilepton_path+dilepton_root_file,Process)
  assert len(ee_up)==len(ee_down)==len(mumu_up)==\
    len(mumu_down)==len(dilepton_up)==len(dilepton_down)\
    ==len(emu_up)==len(emu_down)
  plot_histos(Process)
  
main("ttphoton")
#main("Zphoton")
#main("electronfakes")
#main("hadronfakes")
#main("Other")

