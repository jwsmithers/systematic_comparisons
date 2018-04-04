from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText,TLegend, TF1
from ROOT import gROOT
gROOT.SetBatch(True)

from difflib import SequenceMatcher
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

ejets_path="/afs/cern.ch/work/j/jwsmith/ttgammaPlottingPipeline/build/ejets_fullFit_merged_C_On/build/SR1_ttgamma_SR1_ejets_2018_03/ttgamma_SR1_ejets_2018_03/Histograms/"
ejets_root_file="ttgamma_SR1_ejets_2018_03_event_ELD_MVA_ejets_histos.root"
mujets_path="/afs/cern.ch/work/j/jwsmith/ttgammaPlottingPipeline/build/mujets_fullFit_merged_C_On/build/SR1_ttgamma_SR1_mujets_2018_03/ttgamma_SR1_mujets_2018_03/Histograms/"
mujets_root_file="ttgamma_SR1_mujets_2018_03_event_ELD_MVA_mujets_histos.root"

channels=["mujets","ejets"]

g=globals()
for i in channels:
  g[i+"_nominal"] = []
  g[i+"_up"] = []
  g[i+"_down"] = []


def create_lists(channel,path):
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
    if "_ttphoton_regBin" in i:
      g[channel+"_nominal"].append(i)
    if "Up_regBin" in i:
      g[channel+"_up"].append(i)
    if "Down_regBin" in i:
      g[channel+"_down"].append(i)
  f.Close()

create_lists("ejets", ejets_path+ejets_root_file)
create_lists("mujets",mujets_path+mujets_root_file)


for hist_int in range(0,len(ejets_up)):
  f_ejets = TFile.Open(ejets_path+ejets_root_file, 'read')
  f_mujets = TFile.Open(mujets_path+mujets_root_file, 'read')
  c1 = TCanvas( 'c1', 'Histogram Drawing Options', 0,0,800,800 )
  pad1 = TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
  pad1.SetBottomMargin(0)  # joins upper and lower plot
  pad1.Draw()
  pad2 = TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
  pad2.SetTopMargin(0.0)  # joins upper and lower plot
  pad2.SetBottomMargin(0.2)
  pad2.Draw()
  pad1.cd()

  hist_name_ejets=ejets_up[hist_int]
  hist_name_mujets=mujets_up[hist_int]

  sim = similar(hist_name_ejets,hist_name_mujets)
  if sim < 0.9:
    print hist_name_ejets," and ", hist_name_mujets, " are different!"

  nom_h_ejets = f_ejets.Get(ejets_nominal[0])
  up_h_ejets = f_ejets.Get(ejets_up[hist_int])
  down_h_ejets = f_ejets.Get(ejets_down[hist_int])
  nom_h_mujets = f_mujets.Get(mujets_nominal[0])
  up_h_mujets = f_mujets.Get(mujets_up[hist_int])
  down_h_mujets = f_mujets.Get(mujets_down[hist_int])


  for i in channels:
    y1 = g["nom_h_"+i].GetYaxis()
    y1.SetTitle("Events")
    x1 = g["nom_h_"+i].GetXaxis()
    x1.SetTitle("event level descriminator")

    g["nom_h_"+i].Draw("same")
    g["up_h_"+i].Draw("same")
    g["down_h_"+i].Draw("same")

  up_h_ejets.SetMarkerColor(632)
  up_h_ejets.SetLineColor(632)
  down_h_ejets.SetMarkerColor(857)
  down_h_ejets.SetLineColor(857)

  nom_h_mujets.SetMarkerStyle(4)
  up_h_mujets.SetMarkerColor(632)
  up_h_mujets.SetLineColor(632)
  up_h_mujets.SetMarkerStyle(4)
  down_h_mujets.SetMarkerColor(857)
  down_h_mujets.SetLineColor(857)
  down_h_mujets.SetMarkerStyle(4)


  legend = TLegend(0.15,0.7,0.7,0.85);
  for i in channels:
    legend.AddEntry(g["nom_h_"+i],g[i+"_nominal"][0]+" nominal","lep");
    legend.AddEntry(g["up_h_"+i],g[i+"_up"][0]+" up","lep");
    legend.AddEntry(g["down_h_"+i],g[i+"_down"][0]+" down","lep");


  legend.SetBorderSize(0)
  legend.SetTextSize(0.015)
  legend.Draw();

  c1.Update()

  #### ratio
  pad2.cd()
  ratio1 = nom_h_ejets.Clone("ratio")
  ratio1.SetMinimum(0)
  ratio1.SetMaximum(2)
  ratio1.Sumw2()
  ratio1.SetStats(0)
  ratio1.Divide(up_h_ejets)
  ratio1.SetTitle("")
  y = ratio1.GetYaxis()
  y.SetTitle("#frac{Syst-Nom.}{Nom.} [%]")
  y.SetNdivisions(505)
  #y.SetTitleSize(20)
  #y.SetTitleFont(43)
  y.SetTitleOffset(1.55)
  #y.SetLabelFont(43)
  #y.SetLabelSize(15)
  x = ratio1.GetXaxis()
  x.SetTitle("event level descriminator")
  #x.SetTitleSize(20)
  #x.SetTitleFont(43)
  x.SetTitleOffset(3.2)
  #x.SetLabelFont(43)
  #x.SetLabelSize(15)
  ratio1.SetLineColor(632)
  #ratio1.SetMarkerStyle(20)
  ratio1.SetMarkerColor(632)
  ratio1.Draw("")

  ratio2 = nom_h_ejets.Clone("ratio")
  ratio2.Divide(down_h_ejets)
  ratio2.SetLineColor(857)
  #ratio2.SetMarkerStyle(20)
  ratio2.SetMarkerColor(857)
  ratio2.Draw("same")
  

  line = TF1("fa1","1",-1000,1000);
  line.Draw("same")
  #line.SetLineColor(632);


  c1.SaveAs("histos/"+hist_name_ejets+".pdf")
  del c1
  for i in channels:
    del g["nom_h_"+i]
    del g["up_h_"+i]
    del g["down_h_"+i]
  

