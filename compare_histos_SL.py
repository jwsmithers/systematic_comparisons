from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText,TLegend, TF1, TLatex
from ROOT import gROOT
gROOT.SetBatch(True)
import sys
import os

from difflib import SequenceMatcher
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

ejets_path="/afs/cern.ch/work/j/jwsmith/ttgammaPlottingPipeline/build/ejets_fullFit_merged_C_On/build/SR1_ttgamma_SR1_ejets_2018_03/ttgamma_SR1_ejets_2018_03/Histograms/"
ejets_root_file="ttgamma_SR1_ejets_2018_03_event_ELD_MVA_ejets_histos.root"
mujets_path="/afs/cern.ch/work/j/jwsmith/ttgammaPlottingPipeline/build/mujets_fullFit_merged_C_On/build/SR1_ttgamma_SR1_mujets_2018_03/ttgamma_SR1_mujets_2018_03/Histograms/"
mujets_root_file="ttgamma_SR1_mujets_2018_03_event_ELD_MVA_mujets_histos.root"

singlelepton_path="/afs/cern.ch/work/j/jwsmith/ttgammaPlottingPipeline/build/singlelepton_fullFit_merged_C_On/build/SR1_ejets_mujets_merged/ejets_mujets_merged/Histograms/"
singlelepton_root_file="ejets_mujets_merged_event_ELD_MVA_ejets_histos.root"

channels=["singlelepton","ejets","mujets"]

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
    prefixes=["event_ELD_MVA_ejets_"+process,"event_ELD_MVA_mujets_"+process]
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
  y.SetTitleSize(15)
  x = ratio1.GetXaxis()
  x.SetTitle("event level descriminator")
  x.SetTitleOffset(6.2)
  ratio1.SetLineColor(632)
  ratio1.SetFillColor(632)
  ratio1.SetMarkerColor(632)
  ratio1.SetMarkerStyle(0)
  ratio1.Draw("hist")
  ratio2 = down.Clone("ratio")
  #ratio2.Sumw2()
  ratio2.Add(nom,-1)
  ratio2.Divide(nom)
  ratio2.Scale(100)
  ratio2.SetLineColor(857)
  ratio2.SetFillColor(857)
  ratio2.SetMarkerColor(857)
  ratio2.SetMarkerStyle(0)
  ratio2.Draw("same hist")
  line = TF1("fa1","0",-1000,1000);
  line.SetLineColor(1);
  line.Draw("same")
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
  channel_label = TLatex();
  channel_label.SetNDC();
  channel_label.SetTextAlign(12);
  channel_label.SetTextFont(63);
  channel_label.SetTextSizePixels(15);
  channel_label.DrawLatex(0.45,0.89, channel);
  channel_label.Draw("same")
  return ratio1, ratio2, line, channel_label

def plot_histos(process):
  for hist_int in range(0,len(ejets_up)):
    f_ejets = TFile.Open(ejets_path+ejets_root_file, 'read')
    f_mujets = TFile.Open(mujets_path+mujets_root_file, 'read')
    f_SL = TFile.Open(singlelepton_path+singlelepton_root_file, 'read')
    c1 = TCanvas( 'c1', 'Histogram Drawing Options', 0,0,800,800 )
    pad1 = TPad("pad1", "pad1", 0, 0.49, 1, 1.0)
    pad1.SetBottomMargin(0)  # joins upper and lower plot
    pad1.Draw()
    pad2 = TPad("pad2", "pad2", 0, 0.37, 1, 0.49)
    pad2.SetTopMargin(0.0)  # joins upper and lower plot
    pad2.SetBottomMargin(0)
    pad2.Draw()
    pad3 = TPad("pad3", "pad3", 0, 0.25, 1, 0.37)
    pad3.SetTopMargin(0.0)  # joins upper and lower plot
    pad3.SetBottomMargin(0)
    pad3.Draw()
    pad4 = TPad("pad4", "pad4", 0, 0.05, 1, 0.25)
    pad4.SetTopMargin(0.0)  # joins upper and lower plot
    pad4.SetBottomMargin(0.4)
    pad4.Draw()
    pad1.cd()
  
    hist_name_ejets=ejets_up[hist_int]
    hist_name_mujets=mujets_up[hist_int]
    hist_name_singlelepton=singlelepton_up[hist_int]
  
    sim = similar(hist_name_ejets,hist_name_mujets)
    if "ttphoton_PDF" not in hist_name_ejets:
      if sim < 0.9:
        print hist_name_ejets," and ", hist_name_mujets, " are different!"
        sys.exit()
      sim2 = similar(hist_name_singlelepton,hist_name_ejets)
      # These should be identical
      if sim2 != 1.0:
        print hist_name_singlelepton," and ", hist_name_ejets, " are different!"
        sys.exit()

    g["nom_h_ejets"] = f_ejets.Get(ejets_nominal[0])
    g["up_h_ejets"] = f_ejets.Get(ejets_up[hist_int])
    g["down_h_ejets"] = f_ejets.Get(ejets_down[hist_int])
    g["nom_h_mujets"] = f_mujets.Get(mujets_nominal[0])
    g["up_h_mujets"] = f_mujets.Get(mujets_up[hist_int])
    g["down_h_mujets"] = f_mujets.Get(mujets_down[hist_int])

    g["nom_h_singlelepton"] = f_SL.Get(singlelepton_nominal[0])
    g["up_h_singlelepton"] = f_SL.Get(singlelepton_up[hist_int])
    g["down_h_singlelepton"] = f_SL.Get(singlelepton_down[hist_int])
  
  
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
  
    nom_h_ejets.SetMarkerColor(1)
    nom_h_ejets.SetLineColor(1)
    up_h_ejets.SetMarkerColor(632)
    up_h_ejets.SetLineColor(632)
    down_h_ejets.SetMarkerColor(857)
    down_h_ejets.SetLineColor(857)
  
    nom_h_mujets.SetMarkerStyle(4)
    nom_h_mujets.SetMarkerColor(1)
    nom_h_mujets.SetLineColor(1)
    up_h_mujets.SetMarkerColor(632)
    up_h_mujets.SetLineColor(632)
    up_h_mujets.SetMarkerStyle(4)
    down_h_mujets.SetMarkerColor(857)
    down_h_mujets.SetLineColor(857)
    down_h_mujets.SetMarkerStyle(4)
  
    nom_h_singlelepton.SetMarkerStyle(26)
    nom_h_singlelepton.SetMarkerColor(1)
    nom_h_singlelepton.SetLineColor(1)
    up_h_singlelepton.SetMarkerColor(632)
    up_h_singlelepton.SetLineColor(632)
    up_h_singlelepton.SetMarkerStyle(26)
    down_h_singlelepton.SetMarkerColor(857)
    down_h_singlelepton.SetLineColor(857)
    down_h_singlelepton.SetMarkerStyle(26)
  
    legend = TLegend(0.15,0.4,0.55,0.85);
  
    for i in channels:
      if i=="singlelepton":
        legend.AddEntry(g["nom_h_"+i],g[i+"_nominal"][0].replace("event_ELD_MVA_","").replace("ejets","SL").replace("_regBin","")+" nominal","lep");
        legend.AddEntry(g["up_h_"+i],g[i+"_up"][hist_int].replace("event_ELD_MVA_","").replace("ejets","SL").replace("_regBin",""),"lep");
        legend.AddEntry(g["down_h_"+i],g[i+"_down"][hist_int].replace("event_ELD_MVA_","").replace("ejets","SL").replace("_regBin",""),"lep");
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
    r1=make_ratio(nom_h_ejets,up_h_ejets,down_h_ejets,"e+jets")
    pad3.cd()
    r2=make_ratio(nom_h_mujets,up_h_mujets,down_h_mujets,"#mu+jets")
    pad4.cd()
    r3=make_ratio(nom_h_singlelepton,up_h_singlelepton,down_h_singlelepton,"single lepton")
 

    if not os.path.exists("histos/"+process+"/"):
        os.makedirs("histos/"+process+"/")
  
    c1.SaveAs("histos/"+process+"/"+hist_name_ejets+".pdf")
    del c1
    for i in channels:
      del g["nom_h_"+i]
      del g["up_h_"+i]
      del g["down_h_"+i]
    

def main(Process):
  create_lists("ejets", ejets_path+ejets_root_file,Process)
  create_lists("mujets",mujets_path+mujets_root_file,Process)
  create_lists("singlelepton",singlelepton_path+singlelepton_root_file,Process)
  assert len(ejets_up)==len(ejets_down)==len(mujets_up)==\
    len(mujets_down)==len(singlelepton_up)==len(singlelepton_down)
  plot_histos(Process)
  
main("ttphoton")
#main("QCD")
#main("Wphoton")
#main("electronfakes")
#main("hadronfakes")
#main("Other")

