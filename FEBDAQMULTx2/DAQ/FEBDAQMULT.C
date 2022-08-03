// Mainframe macro generated from application: /home/home/root-6.02.02/bin/root.exe
// By ROOT version 6.02/02 on 2015-05-17 23:03:49

#ifndef ROOT_TGDockableFrame
#include "TGDockableFrame.h"
#endif
#ifndef ROOT_TGMenu
#include "TGMenu.h"
#endif
#ifndef ROOT_TGMdiDecorFrame
#include "TGMdiDecorFrame.h"
#endif
#ifndef ROOT_TG3DLine
#include "TG3DLine.h"
#endif
#ifndef ROOT_TGMdiFrame
#include "TGMdiFrame.h"
#endif
#ifndef ROOT_TGMdiMainFrame
#include "TGMdiMainFrame.h"
#endif
#ifndef ROOT_TGMdiMenu
#include "TGMdiMenu.h"
#endif
#ifndef ROOT_TGListBox
#include "TGListBox.h"
#endif
#ifndef ROOT_TGNumberEntry
#include "TGNumberEntry.h"
#endif
#ifndef ROOT_TGScrollBar
#include "TGScrollBar.h"
#endif
#ifndef ROOT_TGComboBox
#include "TGComboBox.h"
#endif
#ifndef ROOT_TGuiBldHintsEditor
#include "TGuiBldHintsEditor.h"
#endif
#ifndef ROOT_TGuiBldNameFrame
#include "TGuiBldNameFrame.h"
#endif
#ifndef ROOT_TGFrame
#include "TGFrame.h"
#endif
#ifndef ROOT_TGFileDialog
#include "TGFileDialog.h"
#endif
#ifndef ROOT_TGShutter
#include "TGShutter.h"
#endif
#ifndef ROOT_TGButtonGroup
#include "TGButtonGroup.h"
#endif
#ifndef ROOT_TGCanvas
#include "TGCanvas.h"
#endif
#ifndef ROOT_TGFSContainer
#include "TGFSContainer.h"
#endif
#ifndef ROOT_TGuiBldEditor
#include "TGuiBldEditor.h"
#endif
#ifndef ROOT_TGColorSelect
#include "TGColorSelect.h"
#endif
#ifndef ROOT_TGButton
#include "TGButton.h"
#endif
#ifndef ROOT_TGFSComboBox
#include "TGFSComboBox.h"
#endif
#ifndef ROOT_TGLabel
#include "TGLabel.h"
#endif
#ifndef ROOT_TGMsgBox
#include "TGMsgBox.h"
#endif
#ifndef ROOT_TRootGuiBuilder
#include "TRootGuiBuilder.h"
#endif
#ifndef ROOT_TGTab
#include "TGTab.h"
#endif
#ifndef ROOT_TGListView
#include "TGListView.h"
#endif
#ifndef ROOT_TGSplitter
#include "TGSplitter.h"
#endif
#ifndef ROOT_TGStatusBar
#include "TGStatusBar.h"
#endif
#ifndef ROOT_TGListTree
#include "TGListTree.h"
#endif
#ifndef ROOT_TGuiBldGeometryFrame
#include "TGuiBldGeometryFrame.h"
#endif
#ifndef ROOT_TGToolTip
#include "TGToolTip.h"
#endif
#ifndef ROOT_TGToolBar
#include "TGToolBar.h"
#endif
#ifndef ROOT_TRootEmbeddedCanvas
#include "TRootEmbeddedCanvas.h"
#endif
#ifndef ROOT_TCanvas
#include "TCanvas.h"
#endif
#ifndef ROOT_TGuiBldDragManager
#include "TGuiBldDragManager.h"
#endif

#include "Riostream.h"
#include "TBenchmark.h"
#include "TDatime.h"
#include "TGraph.h"
#include "TMath.h"
#include "TF1.h"
#include "TFile.h"
#include "TH2F.h"
#include "TLeaf.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TTree.h"
#include "time.h"
#include <chrono>
#include "rapidjson/document.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"
#include <sys/timeb.h>
#include <unistd.h>
#include <zmq.hpp>
#include "FEBDTP.hxx"

// Namespace for JSON parsing
using namespace rapidjson;

#define maxpe 10 //max number of photoelectrons to use in the fit
#define nboard 2 // number of boards in this system
int NEVDISP=200; //number of lines in the waterfall event display
int nboard_detected = 0; // number of boards detected on the internet
                         // so as to decouple the GUI code from the device code
UShort_t thr_vals[nboard]; // variables to store threshold values for each board
float rate[nboard]; // variables to store trigger rates for each board
int GUI_VERBOSE = 0; // verbosity level of this GUI app
bool QuitScan = false; // a flag for quitting a DAQ loop issued by a parameter scan
float led_Vpp = -1; // a variable for storing the LED driving voltage

const Double_t initpar0[7]={7000,100,700,9.6,1.18,0.3,0.5};
const Double_t initpar1[7]={3470,100,700,9.5,2.25,3e-3,3.7e-2};
Double_t peaks[maxpe]; //positions of peaks in ADC counts
Double_t peaksint[maxpe]; //expected integral of each p.e. peak
UShort_t VCXO_Value=500; //DAC settings to correct onboard VCTCXO
UShort_t VCXO_Values[256]; //DAC settings to correct onboard VCTCXO per board, index=mac5
TGNumberEntry *fNumberEntry75;
TGNumberEntry *fNumberEntry755;
TGNumberEntry *fNumberEntry886;
TGNumberEntry *fNumberEntry8869;
TGNumberEntry *fNumberEntryTME;
//TGLabel *fLabel;
TGStatusBar *fStatusBar739;
//******************************************
TGRadioButton * fChanProbe[nboard][33];
TGCheckButton * fChanEnaAmp[nboard][34];
TGCheckButton * fChanEnaTrig[nboard][33];
TGNumberEntry * fChanGain[nboard][32];
TGNumberEntry * fChanBias[nboard][32];
//******************************************
// TGRadioButton * fChanProbe[33];
// TGCheckButton * fChanEnaAmp[34];
// TGCheckButton * fChanEnaTrig[33];
// TGNumberEntry * fChanGain[32];
// TGNumberEntry * fChanBias[32];
TGCheckButton *fUpdateHisto;
TGCheckButton *fUpdateVCXO;
TGTab *fTab683;
TGLabel *fLabel7;
TBenchmark *BenchMark;
TF1* f0;
TF1* f1;
UChar_t mac5=0x00;
UChar_t bufPMR[1500];
UChar_t bufSCR[1500];
UChar_t buf[1500];
TH1F * hst[nboard][32];
TCanvas *c=0;
TCanvas *c_1=0;
TCanvas *c1=0;
TCanvas *c1_1=0;
TCanvas *c3=0;
TCanvas *c4=0;
TCanvas *c5=0;
TCanvas *c6=0;
TGraph *grevrate=0;
TGraph *gr=0;
TGraph *gts0[256];
TGraph *gts1[256];
TH1F *hcprof=0;
TH2F *hevdisp=0;
void FillHistos(int truncat);
int evs=0; //overall events per DAQ
// int evs_notfirst=0; //overall events per DAQ without very first request
int evsperrequest=0;
FEBDTP* t;
Int_t chan=0; //channel to display on separate canvas c1
Int_t BoardToMon=0; //board to display on separate canvas c1
Int_t slowerBoard = -1; // use the number of events on the slower board
TTree* tr;
int RunOn=0;

time_t tm0,tm1;

uint32_t CHAN_MASK=0xFFFFFFFF; // by default all channels are recorded

//***** ZMQ variables *****
TTimer* timerMsgPoll;
zmq::context_t msgContext(1);
zmq::socket_t msgSocket(msgContext, zmq::socket_type::pair);
std::vector<zmq::pollitem_t> fP;
// variables for storing parameters to scan
std::vector<int> scanFeb1gains;
std::vector<int> scanFeb2gains;

void FEBGUI();
void SetThresholdDAC1(UShort_t dac1);
UShort_t GetThresholdDAC1();
void SetThresholdDAC2(UShort_t dac2);
int Init(const char* iface);
std::string get_current_dir();
float GetTriggerRate();
void UpdateConfig();
void UpdateHisto();
void UpdateBoardMonitor();
void DAQ(int nev);
void RescanNet();
UChar_t ConfigGetGain(int chan);
UChar_t ConfigGetBias(int chan);
void ConfigSetGain(int chan, UChar_t val);
void ConfigSetBias(int chan, UChar_t val);
void ConfigSetFIL(uint32_t mask1, uint32_t mask2, uint8_t majority); 
void ProcessMessage(std::string);

UInt_t GrayToBin(UInt_t n)
{
    UInt_t res=0;
    int a[32],b[32],i=0,c=0,c_1=0;

    for(i=0; i<32; i++){
        if((n & 0x80000000)>0) a[i]=1;
        else a[i]=0;
        n=n<<1;
        //printf("%1d",a[i]);
    }

    b[0]=a[0];
    //printf("  %1d",b[0]);
    for(i=1; i<32; i++){
        if(a[i]>0) if(b[i-1]==0) b[i]=1; else b[i]=0;
        else b[i]=b[i-1];
        //printf("%1d",b[i]);
    }

    for(i=0; i<32; i++){
        res=(res<<1);
        res=(res | b[i]); 
    }
    //printf("\n");

    return res;
}


Double_t mppc0( Double_t *xx, Double_t *par)
{
    Double_t retval=0; //return value 
    Double_t N=par[0]; //normalisation factor
    Double_t gain=par[1]; //adc counts per p.e.
    Double_t zero=par[2]; //position of the pedestal
    Double_t noise=par[3]; //RMS of the electronic noise
    Double_t avnpe=par[4]; //mean number of photoelectrons
    Double_t exess=par[5]; //exess poisson widening factor
    Double_t xtalk=par[6]; //x-talk factor
    Double_t x=xx[0]; //argument  in ADC counts

    for(int i=0; i<maxpe; i++)
    {
        peaks[i]=zero+gain*i;
        peaksint[i]=TMath::Poisson(i,avnpe);
        if(i>=2) peaksint[i]=peaksint[i]+peaksint[i-1]*xtalk;
    }
    for(int i=0; i<maxpe; i++)
    {
        retval+=peaksint[i]*(TMath::Gaus(x,peaks[i],sqrt(noise*noise+i*exess), kTRUE));
        // retval+=TMath::Gaus(x,peaks[i],noise, kTRUE);
    } 
    retval=retval*N;
    return retval;
}

Double_t mppc1( Double_t *xx, Double_t *par) // from http://zeus.phys.uconn.edu/wiki/index.php?title=Characterizing_SiPMs
{
    Double_t retval=0; //return value 
    Double_t N=par[0]; //normalisation factor
    Double_t gain=par[1]; //adc counts per p.e.
    Double_t zero=par[2]; //position of the pedestal
    Double_t noise=par[3]/gain; //normalized RMS of the electronic noise
    Double_t avnpe=par[4]; //mean number of photoelectrons
    Double_t exess=par[5]/gain; //normalized exess poisson widening factor
    Double_t mu=par[6]; //x-talk factor
    Double_t q=(xx[0]-zero)/gain; //argument  in ADC counts normalized and zeroized

    for(int p=0; p<=maxpe; p++) for(int s=0; s<=maxpe; s++)
    {
        retval+= TMath::Poisson(p,avnpe) * TMath::Poisson(s,avnpe*mu) * TMath::Gaus(q,p+s,sqrt(noise*noise+exess*exess*(p+q)), kTRUE);
    }
    retval=retval*N;
    return retval;
}



void FEBDAQMULT(const char *iface="eth1", int verbosity = 0)
{
    if(Init(iface)==0) return;
    GUI_VERBOSE = verbosity; // my utility for debug messages
    FEBGUI();
    UpdateConfig();
    fNumberEntry8869->SetLimitValues(0,t->nclients-1);
    for(int feb=0; feb<t->nclients; feb++)  VCXO_Values[feb]=VCXO_Value;
    // UpdateBoardMonitor();
}

void ConfigSetBit(UChar_t *buffer, UShort_t bitlen, UShort_t bit_index, Bool_t value)
{
    UChar_t byte;
    UChar_t mask;
    byte=buffer[(bitlen-1-bit_index)/8];
    mask= 1 << (7-bit_index%8);
    byte=byte & (~mask);
    if(value) byte=byte | mask;
    buffer[(bitlen-1-bit_index)/8]=byte;
}

bool ConfigGetBit(UChar_t *buffer, UShort_t bitlen, UShort_t bit_index)
{
    UChar_t byte;
    UChar_t mask;
    byte=buffer[(bitlen-1-bit_index)/8];
    mask= 1 << (7-bit_index%8);
    byte=byte & mask;
    if(byte!=0) return true; else return false; 
}

void SendMsg2SlowCtrl(const char* json)
{
    Document document;
    document.Parse(json);
    StringBuffer buffer;
    Writer<StringBuffer> writer(buffer);
    document.Accept(writer);
    std::string msg_str(buffer.GetString());
    zmq::message_t msg_sent(msg_str.size());
    std::memcpy(msg_sent.data(), msg_str.data(), msg_str.size());
    msgSocket.send(msg_sent, zmq::send_flags::none);
}

void SetDstMacByIndex(int i)
{
    if(i>=t->nclients || i<0) return;
    for(int j=0;j<6;j++) t->dstmac[j]=t->macs[i][j];
    mac5=t->macs[i][5];
}


void UpdateConfig()
{
    char bsname[32];
    uint8_t bufFIL[256]; 

    //t->ReadBitStream("CITIROC_SCbitstream_TESTS.txt",bufSCR);
    
    for(int feb=0; feb<t->nclients; feb++)
    {
        int bitlen = 0;
        SetDstMacByIndex(feb);
        t->ReadBitStream("CITIROC_PROBEbitstream.txt",bufPMR);
        // t->dstmac[5]=0xff; //Broadcast
        sprintf(bsname,"CITIROC_SC_SN%03d.txt",t->dstmac[5]);
        //if(!(t->ReadBitStream(bsname,bufSCR))) t->ReadBitStream("CITIROC_SC_DEFAULT.txt",bufSCR);
        if(!(bitlen = t->ReadBitStream(bsname,bufSCR))) bitlen = t->ReadBitStream("CITIROC_SC_PROFILE1.txt",bufSCR);


        *((uint32_t*)(&(bufFIL[0])))=*((uint32_t*)(&(bufSCR[265]))); //copy trigger enable channels from SCR to FIL tregister


        t->SendCMD(t->dstmac,FEB_SET_RECV,fNumberEntry75->GetNumber(),t->srcmac);
        t->SendCMD(t->dstmac,FEB_WR_SCR,0x0000,bufSCR);
        t->SendCMD(t->dstmac,FEB_WR_PMR,0x0000,bufPMR);
        t->SendCMD(t->dstmac,FEB_WR_FIL,0x0000,bufFIL);

        // Print some debug information.
        if(GUI_VERBOSE)
        {
            UChar_t bufPMR_read[1500];
            std::cout << "In UpdateConfig(). BoardToMon value " << BoardToMon << " with MAC address " << (int)t->dstmac[5] << " and VCXO " << fNumberEntry75->GetNumber() << std::endl;
            gROOT->ProcessLine(".! mkdir -p debug");
            t->WriteBitStreamAnnotated(Form("debug/bufSCR%03d.txt", t->dstmac[5]), bufSCR, bitlen);
            // t->SendCMD(t->dstmac, FEB_RD_PMR, 0xFF, bufPMR_read);
            // std::cout << bufPMR_read << std::endl;
            // for(int j = 256; j < 512; j++)std::cout << (int)bufPMR_read[j] << std::endl;
        }

        for(int i=265; i<265+32;i++)
            if(ConfigGetBit(bufSCR,1144,i)) fChanEnaTrig[feb][i-265]->SetOn(); else fChanEnaTrig[feb][i-265]->SetOn(kFALSE);
        if(ConfigGetBit(bufSCR,1144,1139)) fChanEnaTrig[feb][32]->SetOn(); else fChanEnaTrig[feb][32]->SetOn(kFALSE);
        for(int i=0; i<32;i++)
            if(ConfigGetBit(bufSCR,1144,633+i*15)) fChanEnaAmp[feb][i]->SetOn(kFALSE); else fChanEnaAmp[feb][i]->SetOn();
        fChanEnaAmp[feb][33]->SetOn(kFALSE);fChanEnaAmp[feb][32]->SetOn(kFALSE);
        for(int i=0; i<32;i++)
            if(ConfigGetBit(bufPMR,224,96+i)) fChanProbe[feb][i]->SetOn(); else fChanProbe[feb][i]->SetOn(kFALSE);
        
        // read the threshold from file and store it to various containers
        UShort_t thr = GetThresholdDAC1();
        fNumberEntry755->SetNumber(thr);
        for(int feb = 0; feb < t->nclients; feb++) thr_vals[feb] = thr;

        for(int i=0; i<32;i++) fChanGain[feb][i]->SetNumber(ConfigGetGain(i));
        for(int i=0; i<32;i++) fChanBias[feb][i]->SetNumber(ConfigGetBias(i));

    }
    //fNumberEntry755->SetNumber();
}

UChar_t ConfigGetGain(int chan)
{
    UChar_t val=0;
    for(int b=0;b<6;b++)
    {
        val=val << 1;
        if(ConfigGetBit(bufSCR,1144,619+chan*15+b)) val=val+1;
    } 
    return val;
}

UChar_t ConfigGetBias(int chan)
{
    UChar_t val=0;
    for(int b=0;b<8;b++)
    {
        val=val << 1;
        if(ConfigGetBit(bufSCR,1144,331+chan*9+b)) val=val+1;
    } 
    return val;
}

void ConfigSetGain(int chan, UChar_t val)
{
    UChar_t mask=1<<5;
    for(int b=0;b<6;b++)
    {
        if((val & mask)>0) ConfigSetBit(bufSCR,1144,619+chan*15+b,kTRUE); else ConfigSetBit(bufSCR,1144,619+chan*15+b,kFALSE);
        mask=mask>>1;
    } 

}

// Bring up a control application for power unit, etc.
void ControlApp()
{
    // find the project's root folder and the script to run
    std::string proj_root = get_current_dir();
    if(proj_root.find("FEBDAQMULTx2") > 0)
        proj_root = proj_root.substr(0, proj_root.find("FEBDAQMULTx2")+12);
    else // if the standard path is not found, use relative path and hope for the best
        proj_root = std::string("..");
    
    // The following command does not work because the script is run with
    // superuser which does not have anaconda set up by default.
    // std::string script_fpn = proj_root + "/slow-control/main_control.py";
    // std::string cmd = "sudo -u hepr2018 python " + script_fpn + " &";

    // Use a bash script instead that sets up the environment before running the
    // main python script.
    std::string script_fpn = proj_root + "/slow-control/setup_and_run.sh";
    std::string cmd = "bash " + script_fpn + " &";
    gSystem->Exec(cmd.c_str());
}

void ConfigSetBias(int chan, UChar_t val)
{
    UChar_t mask=1<<7;
    for(int b=0;b<8;b++)
    {
        if((val & mask)>0) ConfigSetBit(bufSCR,1144,331+chan*9+b,kTRUE); else ConfigSetBit(bufSCR,1144,331+chan*9+b,kFALSE);
        mask=mask>>1;
    } 

}



void PollMessage()
{
    // std::cout << "hi" << std::endl;
    zmq::message_t message;
    zmq::poll(fP.data(), 1, 0); // changed from zmq::poll(fP.data(), 2, 1); So far no segfault...
    
    if (fP[0].revents & ZMQ_POLLIN) {
        zmq::recv_result_t rec_res = msgSocket.recv(message, zmq::recv_flags::dontwait);
        //  Process task
        std::string rpl = std::string(static_cast<char*>(message.data()), message.size());
        std::cout << "DAQ receiving " << rpl << std::endl;
        ProcessMessage(rpl);
    }
}




void PrintConfig(UChar_t *buffer, UShort_t bitlen)
{
    UChar_t byte;
    UChar_t mask;
    for(int i=0; i<bitlen;i++)
    {
        byte=buffer[(bitlen-1-i)/8];
        mask= 1 << (7-i%8);
        byte=byte & mask;
        if(byte==0) printf("0"); else printf("1");
    }
    printf("\n"); 
} 

void SendConfig()
{
    uint32_t trigmask=0;
    uint8_t bufFIL[256]; 

    int curBoard = BoardToMon;

    for(int feb=0; feb<t->nclients; feb++)
    {
    
        // t->dstmac[5]=0xff; //Broadcast
        // specify the board to configure
        SetDstMacByIndex(feb);

        for(int i=265; i<265+32;i++)
            if(fChanEnaTrig[feb][i-265]->IsOn()) ConfigSetBit(bufSCR,1144,i,1); else  ConfigSetBit(bufSCR,1144,i,0);

        if(fChanEnaTrig[feb][32]->IsOn()) ConfigSetBit(bufSCR,1144,1139,1); else  ConfigSetBit(bufSCR,1144,1139,0); //OR32 enable

        for(int i=0; i<32;i++)
            if(fChanEnaAmp[feb][i]->IsOn()) ConfigSetBit(bufSCR,1144,633+i*15,0); else  ConfigSetBit(bufSCR,1144,633+i*15,1);

        for(int i=0; i<32;i++)
            if(fChanProbe[feb][i]->IsOn()) ConfigSetBit(bufPMR,224,96+i,1); else  ConfigSetBit(bufPMR,224,96+i,0);

        for(int i=0; i<32;i++) ConfigSetBias(i, fChanBias[feb][i]->GetNumber());
        for(int i=0; i<32;i++) ConfigSetGain(i, fChanGain[feb][i]->GetNumber());

        for(int i=0; i<32;i++)
            if(fChanEnaTrig[feb][i]->IsOn()) trigmask = trigmask | (0x1 << i);
        *((uint32_t*)(&(bufFIL[0])))=trigmask;

        t->SendCMD(t->dstmac,FEB_WR_SCR,0x0000,bufSCR);
        t->SendCMD(t->dstmac,FEB_WR_PMR,0x0000,bufPMR);
        t->SendCMD(t->dstmac,FEB_WR_FIL,0x0000,bufFIL);
    }

    BoardToMon = curBoard;

    if(GUI_VERBOSE)
        std::cout << "SendConfig() is called. Configuration should be sent." << std::endl;
}

void SendConfig2All()
{
    Int_t curBoard = BoardToMon;
    for(int feb = 0; feb < t->nclients; feb++)
    {
        BoardToMon = feb;
        SendConfig();
    }
    BoardToMon = curBoard;
}

void SaveAsDialog()
{
    // check if a tree exists already
    if(!tr)
    {
        std::cout << "No data to save!" << std::endl;
        return;
    }

    // define some variables
    const char *rcfiletypes[] = {
        "All files",     "*",
        0,               0
    };
    char* rcdir = (char*)".";
    char* rcfile = (char*)".everc";

    TGFileInfo fi;
    fi.fFileTypes = rcfiletypes;
    fi.fIniDir = rcdir;
    fi.fFilename = rcfile;
    std::cout << "1 " << fi.fFilename << std::endl;
    new TGFileDialog(gClient->GetRoot(), gClient->GetRoot(), kFDSave, &fi);
    // new TGFileDialog(0, 0, kFDSave, &fi);
    std::cout << "2 " << fi.fFilename << std::endl;
    if (fi.fFilename) {
        rcfile = fi.fFilename;
    }
    rcdir = fi.fIniDir;
    std::cout << "3 " << fi.fFilename << std::endl;
    // save tree to file
    // tr->SaveAs(fi.fFilename);
}

void SaveMetadata(std::string outfpn, float v_bias, float temper)
{
    Int_t board;
    Int_t channel;
    Float_t DAC;
    Bool_t isTrigger;
    Int_t preampGain;
    Int_t channelBias;
    Float_t biasVoltage;
    Float_t temperature;
    Float_t ledVpp;

    TFile f(outfpn.c_str(), "update");
    TTree* tr_meta = new TTree("metadata", "A tree for configuration parameters");
    tr_meta->Branch("board", &board, "board/I");
    tr_meta->Branch("channel", &channel, "channel/I");
    tr_meta->Branch("DAC", &DAC, "DAC/F");
    tr_meta->Branch("isTrigger", &isTrigger, "isTrigger/O");
    tr_meta->Branch("preampGain", &preampGain, "preampGain/I");
    tr_meta->Branch("channelBias", &channelBias, "channelBias/I");
    tr_meta->Branch("biasVoltage", &biasVoltage, "biasVoltage/F");
    tr_meta->Branch("temperature", &temperature, "temperature/F");
    tr_meta->Branch("ledVpp", &ledVpp, "ledVpp/F");

    // fill the metadata tree
    for(int i = 0; i < t->nclients; i++)
        for(int j = 0; j < 32; j++)
        {
            board = i;
            channel = j;
            DAC = thr_vals[i];
            isTrigger = fChanEnaTrig[i][j]->IsOn();
            preampGain = fChanGain[i][j]->GetNumber();
            channelBias = fChanBias[i][j]->GetNumber();
            biasVoltage = v_bias;
            temperature = temper;
            ledVpp = led_Vpp;
            tr_meta->Fill();
        }
    f.cd();
    tr_meta->Write();
    f.Close();
}

void SaveToFile(std::string outfpn)
{
    tr->SaveAs(outfpn.c_str());

    // make a tree to store metadata of the configuration parameters
    SaveMetadata(outfpn, -1, -1);
}

extern "C" {
    void SelectBoard()
    {
        if(fTab683->GetCurrent() <= 6) BoardToMon = 0;
        else BoardToMon = 1;
        fNumberEntry8869->SetNumber(BoardToMon); // number entry for board ID
        fNumberEntry755->SetNumber(thr_vals[BoardToMon]); // number entry for threshold setting
        UpdateBoardMonitor();

        // show most recent trigger rate stored
        // set color according to the rate
        if(rate[BoardToMon]<3.6) fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xbbffbb);
        else if (rate[BoardToMon]<5.0) fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xffbbbb);
        else if (rate[BoardToMon]<7.0) fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xff9999);
        else if (rate[BoardToMon]<10.0) fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xff7777);
        else fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xff3333);
        // show the rate
        char str1[64];
        sprintf(str1,"Trigger %2.3f kHz",rate[BoardToMon]);
        fStatusBar739->SetText(str1, 0);
    }
}

void SendAllChecked()
{
    for(int i=0; i<32;i++)
    {
        fChanEnaAmp[BoardToMon][i]->SetOn(); 
        ConfigSetBit(bufSCR,1144,633+i*15,0); 
    }

    SetDstMacByIndex(BoardToMon);  
    //t->dstmac[5]=0xff; //Broadcast
    t->SendCMD(t->dstmac,FEB_WR_SCR,0x0000,bufSCR);
    //  t->SendCMD(t->dstmac,FEB_WR_PMR,0x0000,bufPMR);
    // }
    fChanEnaAmp[BoardToMon][33]->SetOn(kFALSE);fChanEnaAmp[BoardToMon][32]->SetOn(kFALSE);
}
void SendAllUnChecked()
{
    for(int i=0; i<32;i++)
    {
        fChanEnaAmp[BoardToMon][i]->SetOn(kFALSE); 
        ConfigSetBit(bufSCR,1144,633+i*15,1); 
    }

    SetDstMacByIndex(BoardToMon);  
    //t->dstmac[5]=0xff; //Broadcast
    t->SendCMD(t->dstmac,FEB_WR_SCR,0x0000,bufSCR);
    //  t->SendCMD(t->dstmac,FEB_WR_PMR,0x0000,bufPMR);
    // }
    fChanEnaAmp[BoardToMon][33]->SetOn(kFALSE);
    fChanEnaAmp[BoardToMon][32]->SetOn(kFALSE);
}




UShort_t chg[32];
UInt_t ts0,ts1;
UInt_t ts0_ref, ts1_ref;
UInt_t ts0_ref_MEM[256], ts1_ref_MEM[256]; //memorized time stamps for all febs
long int ts0_ref_AVE[256]; //Average value for PPS ts0, used for VCXO feedback
Int_t ts0_ref_IND[256]; //Number of averaged values for PPS ts0, used for VCXO feedback
Bool_t NOts0=false,NOts1=false;
UInt_t ts0_ref_mon, ts1_ref_mon;
Bool_t NOts0_mon=false,NOts1_mon=false;
//UChar_t mac5=0x00;
Long_t ns_epoch; // My variable. Nanoseconds since epoch.
Float_t trig_rate;

void RescanNet()
{
    t->nclients=0;
    if(t->ScanClients()==0) {printf("No clients connected, exiting\n"); return;}; 
    t->PrintMacTable();
    t->VCXO=500;
    for(int feb=0; feb<t->nclients; feb++)  { ts0_ref_AVE[t->macs[feb][5]]=0;ts0_ref_IND[t->macs[feb][5]]=0; }
    UpdateConfig();
    fNumberEntry8869->SetLimitValues(0,t->nclients-1);
    for(int feb=0; feb<t->nclients; feb++)  VCXO_Values[feb]=VCXO_Value;
    // UpdateBoardMonitor();

}


int Init(const char *iface="eth1")
{
    t=new FEBDTP(iface);
    if(t->ScanClients()==0) {printf("No clients connected, exiting\n"); return 0;};
    t->PrintMacTable(); 

    t->VCXO=500;
    for(int feb=0; feb<t->nclients; feb++)  { ts0_ref_AVE[t->macs[feb][5]]=0;ts0_ref_IND[t->macs[feb][5]]=0; }
    // Store the number of detected clients for other parts of the code.
    nboard_detected = t->nclients;

    t->setPacketHandler(&FillHistos);
    char str1[32];
    char str2[32];
    SetDstMacByIndex(0);
    evs=0;
    for(int i=0;i<32;i++)
        for(int feb = 0; feb < nboard; feb++)
        {
            sprintf(str1,"h%d_%d",i, feb);
            sprintf(str2,"ADC # %d",i);
            hst[feb][i]=new TH1F(str1,str2,820,0,4100);
            hst[feb][i]->GetXaxis()->SetTitle("ADC value");
            hst[feb][i]->GetYaxis()->SetTitle("Events");
        }
    for(int i=0;i<256;i++) gts0[i]=new TGraph();
    for(int i=0;i<256;i++) gts1[i]=new TGraph();
    hcprof=new TH1F("hcprof","Channel profile",32,0,32);
    hcprof->GetXaxis()->SetTitle("Channel number");
    hcprof->GetYaxis()->SetTitle("Integrated amplitude, ADC");
    hevdisp=new TH2F("hevdisp","Event Display",32,0,32,NEVDISP,0,NEVDISP);
    hevdisp->GetXaxis()->SetTitle("Channel number");
    hevdisp->GetYaxis()->SetTitle("Event number");
    grevrate= new TGraph();
    f0=new TF1("mppc0",mppc0,0,2000,7);
    f0->SetParameters(initpar0);
    f0->SetNpx(1000);
    f0->SetParNames("Norm","Gain","Pedestal","NoiseRMS","Npe","exess","X-talk");
    f1=new TF1("mppc1",mppc1,0,2000,7);
    f1->SetParameters(initpar1);
    f1->SetNpx(1000);
    f1->SetParNames("Norm","Gain","Pedestal","NoiseRMS","Npe","exess","X-talk");
    f1->SetLineColor(kBlue);
    tr=new TTree("mppc","mppc");
    tr->Branch("mac5",&mac5,"mac5/b");
    tr->Branch("chg",chg,"chg[32]/s");
    tr->Branch("ts0",&ts0,"ts0/i");
    tr->Branch("ts1",&ts1,"ts1/i");
    tr->Branch("ts0_ref",&ts0_ref,"ts0_ref/i");
    tr->Branch("ts1_ref",&ts1_ref,"ts1_ref/i");
    tr->Branch("ns_epoch", &ns_epoch, "ns_epoch/L");
    tr->Branch("trig_rate", &trig_rate, "trig_rate/F");

    BenchMark=new TBenchmark();
    BenchMark->Start("Poll");
    // initialize the threshold container variable
    for(int feb = 0; feb < nboard; feb++) thr_vals[feb] = 0;


    //***** ZMQ business *****
    // try to bind the socket
    try {
        msgSocket.bind("tcp://*:5556");
        fP.push_back({ static_cast<void*>(msgSocket), 0, ZMQ_POLLIN, 0 });
    }
    catch (...){
        std::cout << "Socket related errors..." << std::endl;
    }
    // initialize a timer to poll the ZMQ message queue
    timerMsgPoll = new TTimer();
    timerMsgPoll->Connect("Timeout()", 0, 0, "PollMessage()");
    timerMsgPoll->Start(1000, kFALSE);
    //***** ZMQ business *****

    return 1;
}

UInt_t overwritten=0;
UInt_t lostinfpga=0;
UInt_t total_lost=0;

void FillHistos(int truncat)  // hook called by libFEBDTP when event is received
{
    int jj;
    int kk;
    //UInt_t T0,T1;
    UShort_t adc;
    int evspack=0;
    UInt_t tt0,tt1;
    UChar_t ls2b0,ls2b1; //least sig 2 bits

    jj=0;
    while(jj<truncat-18)
    {
        //printf(" Remaining events: %d\n",(t->gpkt).REG);
        //printf("Flags: 0x%08x ",*(UInt_t*)(&(t->gpkt).Data[jj]));
        overwritten=*(UShort_t*)(&(t->gpkt).Data[jj]); 
        jj=jj+2;
        lostinfpga=*(UShort_t*)(&(t->gpkt).Data[jj]); 
        jj=jj+2;
        ts0=*(UInt_t*)(&(t->gpkt).Data[jj]); jj=jj+4; 
        ts1=*(UInt_t*)(&(t->gpkt).Data[jj]); jj=jj+4; 
        //	printf("T0=%u ns, T1=%u ns \n",ts0,ts1);
        ls2b0=ts0 & 0x00000003;
        ls2b1=ts1 & 0x00000003;
        tt0=(ts0 & 0x3fffffff) >>2;
        tt1=(ts1 & 0x3fffffff) >>2;
        tt0=(GrayToBin(tt0) << 2) | ls2b0;
        tt1=(GrayToBin(tt1) << 2) | ls2b1;
        tt0=tt0+5;//IK: correction based on phase drift w.r.t GPS
        tt1=tt1+5; //IK: correction based on phase drift w.r.t GPS
        NOts0=((ts0 & 0x40000000)>0); // check overflow bit
        NOts1=((ts1 & 0x40000000)>0);
        if((ts0 & 0x80000000)>0) {ts0=0x0; ts0_ref=tt0; ts0_ref_MEM[t->dstmac[5]]=tt0; 
            ts0_ref_AVE[t->dstmac[5]]=ts0_ref_AVE[t->dstmac[5]]+ts0_ref_MEM[t->dstmac[5]]; (ts0_ref_IND[t->dstmac[5]])++;} 
        else { ts0=tt0; ts0_ref=ts0_ref_MEM[t->dstmac[5]]; }
        if((ts1 & 0x80000000)>0) {ts1=0x0; ts1_ref=tt1; ts1_ref_MEM[t->dstmac[5]]=tt1;} else { ts1=tt1; ts1_ref=ts1_ref_MEM[t->dstmac[5]]; }

        if(t->Verbose) printf("T0=%u ns, T1=%u ns T0_ref=%u ns  T1_ref=%u ns \n",ts0,ts1,ts0_ref,ts1_ref);
        //	printf(" ADC[32]:\n"); 

        for(kk=0; kk<32; kk++)
            if (CHAN_MASK & (1<<kk))
            {
                adc=*(UShort_t*)(&(t->gpkt).Data[jj]); jj++; jj++;  
                //		printf("%04u ",adc);
                
                // Loop through all devices and put data to corresponding containers.
                for(int feb = 0; feb < t->nclients; feb++)
                {
                    // SetDstMacByIndex(feb);
                    if(t->dstmac[5] == t->macs[feb][5])
                    { 
                        hst[feb][kk]->Fill(adc);
                        hcprof->Fill(kk,adc);
                        if(fUpdateHisto->IsOn() && fTab683->GetCurrent()==6) {   
                            hevdisp->SetBinContent(kk,NEVDISP,adc);
                        }
                    }
                }
                // SetDstMacByIndex(BoardToMon);
                chg[kk]=adc;
            } //if(jj>=(truncat-18)) return;}
            else {chg[kk]=0; jj+=2;}

        if(t->dstmac[5] == t->macs[BoardToMon][5]) 
            if(fUpdateHisto->IsOn() && fTab683->GetCurrent()==6) {   
                for(int evi=1; evi<=NEVDISP;evi++) for(kk=0; kk<32; kk++)
                {
                    hevdisp->SetBinContent(kk,evi-1,hevdisp->GetBinContent(kk,evi));
                }
            }

        //       printf("\n");
        mac5=t->dstmac[5];
        // printf("Filling tree with mac5=0x%02x\n",mac5);
        gts0[mac5]->SetPoint(gts0[mac5]->GetN(),gts0[mac5]->GetN(),ts0_ref-1e9);
        if(ts1!=0) gts1[mac5]->SetPoint(gts1[mac5]->GetN(),gts1[mac5]->GetN(),ts1);

        // before fill the tree, store the time stamp as recorded by the current application
        auto curtime = std::chrono::high_resolution_clock::now();
        ns_epoch = curtime.time_since_epoch().count();
        // store the instantaneous trigger rate
        trig_rate = 0;
        for(int bid = 0; bid < t->nclients; bid++)
            if(t->dstmac[5] == t->macs[bid][5])
                trig_rate = rate[bid];
        tr->Fill();
        if(t->dstmac[5] == t->macs[slowerBoard][5])
        {
            evs++;
            evspack++; 
            evsperrequest++; 
            total_lost+=lostinfpga; 
            ts0_ref_mon=ts0_ref;  
            ts1_ref_mon=ts1_ref;
            NOts0_mon=NOts0;  
            NOts1_mon=NOts1;  
        }
    }
    // printf("Packet: events %d\n", evspack);

}

void UpdateHisto()
{
    chan=fNumberEntry886->GetNumber();
    for(int y=0;y<8;y++) for(int x=0;x<4;x++) {c->cd(y*4+x+1); gPad->SetLogy(); hst[0][y*4+x]->Draw();}
    c->Update();
    for(int y=0;y<8;y++) for(int x=0;x<4;x++) {c_1->cd(y*4+x+1); gPad->SetLogy(); hst[1][y*4+x]->Draw();}
    c_1->Update();
    c1->cd(); hst[0][chan]->Draw();
    c1->Update();
    c1_1->cd(); hst[1][chan]->Draw();
    c1_1->Update();
    c3->cd(1);
    gts0[t->macs[0][5]]->Draw("AL");
    gts0[t->macs[0][5]]->GetHistogram()->GetYaxis()->SetRangeUser(-100,100);
    gts0[t->macs[0][5]]->GetHistogram()->GetXaxis()->SetTitle("Event number");
    gts0[t->macs[0][5]]->GetHistogram()->GetYaxis()->SetTitle("TS0 period deviation from 1s, ns");
    for(int feb=0; feb<t->nclients; feb++)  { gts0[t->macs[feb][5]]->Draw("sameL"); }    
    c3->cd(2);
    gts1[t->macs[0][5]]->Draw("AL");
    gts1[t->macs[0][5]]->GetHistogram()->GetXaxis()->SetTitle("Event number");
    gts1[t->macs[0][5]]->GetHistogram()->GetYaxis()->SetTitle("TS1, ns");
    //gts0[t->macs[0][5]]->GetHistogram()->GetYaxis()->SetRangeUser(-100,100);
    for(int feb=0; feb<t->nclients; feb++)  { gts1[t->macs[feb][5]]->Draw("sameL"); }    
    c3->Update();
    c4->cd();
    hcprof->Draw("hist");
    c4->Update();
    c5->cd();
    grevrate->Draw("AL");
    grevrate->GetHistogram()->GetXaxis()->SetTitle("Poll Nr.");
    grevrate->GetHistogram()->GetYaxis()->SetTitle("Event rate, kHz");
    c5->Update();
    c6->cd();
    hevdisp->Draw("colz");
    c6->Update();

}

void StopDAQ()
{
    t->dstmac[5]=0xff; //Broadcast
    t->SendCMD(t->dstmac,FEB_GEN_INIT,0,buf);  
}


// nev: number of events to take
void StartDAQ(int nev=0)
{
    t->dstmac[5]=0xff; //Broadcast
    t->SendCMD(t->dstmac,FEB_GEN_INIT,1,buf); //reset buffer
    t->SendCMD(t->dstmac,FEB_GEN_INIT,2,buf); //set DAQ_Enable flag on FEB
    DAQ(nev);
    RunOn=0;
    StopDAQ();
}


void DAQ(int nev=0)
{
    char str1[64];
    char str2[32];
    evs=0;
    int nevv=nev;
    double avts0;
    int deltaVCXO;
    // evs_notfirst=0;
    int notok=0;
    int ok=0;
    //  bool first_request=true;
    total_lost=0;
    RunOn=1;
    float PollPeriod;
    //  UpdateConfig();
    // t->SendCMD(t->dstmac,FEB_GEN_HVON,0,buf);
    // printf("nevv=%d, evs=%d\n",nevv,evs);
    tm0=time(NULL);
    tm1=time(NULL);
    while(RunOn==1 && (nevv==0 || evs<nevv) && (fNumberEntryTME->GetNumber()==0 || tm1-tm0 < fNumberEntryTME->GetNumber() ))
    {

        // printf("nevv=%d, evs=%d\n",nevv,evs);
        BenchMark->Show("Poll");
        PollPeriod=BenchMark->GetRealTime("Poll");
        BenchMark->Reset();
        BenchMark->Start("Poll");
        //Perform VCXO correction
        if(GUI_VERBOSE) std::cout << "Perform VCXO correction." << std::endl;
        for(int feb=0; feb<t->nclients; feb++)
        { 
            if(ts0_ref_IND[t->macs[feb][5]]>=20) 
            { //correct one FEB VCXO
                avts0=ts0_ref_AVE[t->macs[feb][5]] / ts0_ref_IND[t->macs[feb][5]];
                deltaVCXO=-(avts0-1e9)/5.2; //derive correction increment, approx 5.2 ns per DAC LSB
                //   printf("Average period %f\n",avts0);
                VCXO_Values[feb]=VCXO_Values[feb]+deltaVCXO;
                ts0_ref_AVE[t->macs[feb][5]]=0;ts0_ref_IND[t->macs[feb][5]]=0; 
                if(fUpdateVCXO->IsOn()) {
                    printf("------------------ For board %d : Average period %f, Set VCXO  (0x%02x) to %d (+%d)\n",feb,avts0, t->macs[feb][5], VCXO_Values[feb],deltaVCXO);
                    t->VCXO=VCXO_Values[feb];
                    t->SendCMD(t->macs[feb],FEB_SET_RECV,VCXO_Values[feb],t->srcmac);
                }
            }

        }
        chan=fNumberEntry886->GetNumber(); // choose a single channel to monitor
        // calculate rates for both channels
        int btm_now = BoardToMon;
        for(int bItr = 0; bItr < nboard; bItr++)
        {
            BoardToMon = bItr;
            rate[BoardToMon] = GetTriggerRate()/1e3;
        }
        BoardToMon = btm_now;
        // calculate rates for both channels
        sprintf(str1,"Trigger %2.3f kHz",rate[BoardToMon]);
        grevrate->SetPoint(grevrate->GetN(),grevrate->GetN(),rate[BoardToMon]);

        // Determine the slower board
        // if(slowerBoard < 0)
        // {
            // normal conditions
            slowerBoard = 0;
            // If FEB1 has zero rate, count event with FEB2.
            // Or, if FEB2 has a lower but non-zero rate, count event with FEB2.
            if(((rate[1] < rate[0]) && (rate[1] > 1e-8)) || (rate[0] < 1e-8))
                slowerBoard = 1;
            // std::cout << "rates: " << rate[0] << " " << rate[1] << std::endl;
        // }

        if(rate[BoardToMon]<3.6) fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xbbffbb);
        else if (rate[BoardToMon]<5.0) fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xffbbbb);
        else if (rate[BoardToMon]<7.0) fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xff9999);
        else if (rate[BoardToMon]<10.0) fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xff7777);
        else fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xff3333);

        //    fLabel->SetText(str1);
        if(GUI_VERBOSE) std::cout << "Event buffer data request..." << std::endl;
        fStatusBar739->SetText(str1,0);
        for(int feb=0; feb<t->nclients; feb++)
        {
            SetDstMacByIndex(feb);
            mac5=t->dstmac[5];
            ok=t->SendCMD(t->dstmac,FEB_RD_CDR,0,buf);
        }
        if(GUI_VERBOSE) std::cout << "Successfully sent data request to event buffer." << std::endl;

        if(fUpdateHisto->IsOn() && fTab683->GetCurrent()==1) {   
            for(int y=0;y<8;y++) for(int x=0;x<4;x++) {c->cd(y*4+x+1); gPad->SetLogy(); hst[0][y*4+x]->Draw();}
            c->Update();
        }
        if(fUpdateHisto->IsOn() && fTab683->GetCurrent()==2) {   
            c1->cd(); hst[0][chan]->Draw();
            c1->Update();
        }
        if(fUpdateHisto->IsOn() && fTab683->GetCurrent()==3) {   
            c3->cd(1);
            gts0[t->macs[0][5]]->Draw("AL");
            gts0[t->macs[0][5]]->GetHistogram()->GetXaxis()->SetTitle("Event number");
            gts0[t->macs[0][5]]->GetHistogram()->GetYaxis()->SetTitle("TS0 period deviation from 1s, ns");

            gts0[t->macs[0][5]]->GetHistogram()->GetYaxis()->SetRangeUser(-100,100);
            for(int feb=0; feb<t->nclients; feb++)  { gts0[t->macs[feb][5]]->Draw("sameL"); }    
            c3->cd(2);
            gts1[t->macs[0][5]]->Draw("AL");
            gts1[t->macs[0][5]]->GetHistogram()->GetXaxis()->SetTitle("Event number");
            gts1[t->macs[0][5]]->GetHistogram()->GetYaxis()->SetTitle("TS1, ns");

            //gts0[t->macs[0][5]]->GetHistogram()->GetYaxis()->SetRangeUser(-100,100);
            for(int feb=0; feb<t->nclients; feb++)  { gts1[t->macs[feb][5]]->Draw("sameL"); }    
            c3->Update();
        }
        if(fUpdateHisto->IsOn() && fTab683->GetCurrent()==4) {   
            c4->cd();
            hcprof->Draw("hist");
            c4->Update();
        }
        if(fUpdateHisto->IsOn() && fTab683->GetCurrent()==5) {   
            c5->cd();
            grevrate->Draw("AL");
            grevrate->GetHistogram()->GetXaxis()->SetTitle("Poll Nr.");
            grevrate->GetHistogram()->GetYaxis()->SetTitle("Event rate, kHz");
            c5->Update();
        }
        if(fUpdateHisto->IsOn() && fTab683->GetCurrent()==6) {   
            c6->cd();
            hevdisp->Draw("colz");
            c6->Update();
        }
        if(fUpdateHisto->IsOn() && fTab683->GetCurrent()==8) {
            for(int y=0;y<8;y++) for(int x=0;x<4;x++) {c_1->cd(y*4+x+1); gPad->SetLogy(); hst[1][y*4+x]->Draw();}
            c_1->Update();
        }
        if(fUpdateHisto->IsOn() && fTab683->GetCurrent()==9) {   
            c1_1->cd(); hst[1][chan]->Draw();
            c1_1->Update();
        }



        gSystem->ProcessEvents();
        printf("Per request: %d events acquired, overwritten (flags field of last event) %d\n",evsperrequest,overwritten);
        if(nevv>0) printf("%d events to go...\n",nevv-evs);
        sprintf(str1,"Poll: %d events acquired in %2.2f sec.",evsperrequest,PollPeriod);
        if(evsperrequest>0) fStatusBar739->GetBarPart(1)->SetBackgroundColor(0xbbffbb);
        else fStatusBar739->GetBarPart(1)->SetBackgroundColor(0xffaaaa);

        fStatusBar739->SetText(str1,1);
        sprintf(str1,"Evs lost FPGA:%d CPU:%d ",lostinfpga,overwritten);
        if(overwritten==0) fStatusBar739->GetBarPart(2)->SetBackgroundColor(0xbbffbb);
        else if (overwritten<10) fStatusBar739->GetBarPart(2)->SetBackgroundColor(0xffbbbb);
        else if (overwritten<100) fStatusBar739->GetBarPart(2)->SetBackgroundColor(0xff9999);
        else if (overwritten<1000) fStatusBar739->GetBarPart(2)->SetBackgroundColor(0xff7777);
        else fStatusBar739->GetBarPart(2)->SetBackgroundColor(0xff3333);
        fStatusBar739->SetText(str1,2);
        if(NOts0_mon) { sprintf(str1,"PPS missing!"); fStatusBar739->GetBarPart(3)->SetBackgroundColor(0xffaaaa);} 
        else { sprintf(str1,"PPS period %d ns",ts0_ref_mon); fStatusBar739->GetBarPart(3)->SetBackgroundColor(0xbbffbb);} 
        fStatusBar739->SetText(str1,3);
        if(NOts1_mon) { sprintf(str1,"SPILL trig missing!"); fStatusBar739->GetBarPart(4)->SetBackgroundColor(0xffaaaa);} 
        else { sprintf(str1,"SPILL trig period %d ns",ts1_ref_mon);fStatusBar739->GetBarPart(4)->SetBackgroundColor(0xbbffbb);} 
        fStatusBar739->SetText(str1,4);
        sprintf(str1, "Overal: %d acquired, %d (%2.1f\%%) lost",evs,total_lost, (100.*total_lost/(evs+total_lost)));
        fStatusBar739->SetText(str1,5);

        //         if(first_request ) {first_request=false; total_lost=0;}
        total_lost+=overwritten; //evs_notfirst+=evsperrequest; }//skip lost events from the very first request
        //     if(evsperrequest==0) first_request== true;
        //      printf("Debug: total_lost=%d \n",total_lost);
        overwritten=0;
        evsperrequest=0;
        tm1=time(NULL);

    } // One of the escaping condition from the while loop is RunOn==0,
      // Which can be trigger by pressing the Stop DAQ button.

    fStatusBar739->GetBarPart(0)->SetBackgroundColor(0xffffff); 
    fStatusBar739->GetBarPart(1)->SetBackgroundColor(0xffffff); 
    fStatusBar739->GetBarPart(2)->SetBackgroundColor(0xffffff); 
    fStatusBar739->GetBarPart(3)->SetBackgroundColor(0xffffff); 
    fStatusBar739->GetBarPart(4)->SetBackgroundColor(0xffffff); 
    fStatusBar739->GetBarPart(5)->SetBackgroundColor(0xffffff); 

    // t->SendCMD(t->dstmac,FEB_GEN_HVOF,0,buf);
    printf("Overal per DAQ call: %d events acquired, %d (%2.1f\%%) lost (skipping first request).\n",evs,total_lost, (100.*total_lost/(evs+total_lost)));
    sprintf(str1, "Overal: %d acquired, %d (%2.1f\%%) lost",evs,total_lost, (100.*total_lost/(evs+total_lost)));
    fStatusBar739->SetText(str1,5);

    // Update all histogram tab after a run is stopped.
    for(int y=0;y<8;y++) for(int x=0;x<4;x++) {c->cd(y*4+x+1); gPad->SetLogy(); hst[0][y*4+x]->Draw();}
    c->Update();
    for(int y=0;y<8;y++) for(int x=0;x<4;x++) {c_1->cd(y*4+x+1); gPad->SetLogy(); hst[1][y*4+x]->Draw();}
    c_1->Update();

}

void Reset()
{
    for(int y=0;y<8;y++) for(int x=0;x<4;x++) { hst[0][y*4+x]->Reset(); hst[1][y*4+x]->Reset();}
    c1->cd(); hst[0][chan]->Draw();
    c1->Update();
    c1_1->cd(); hst[1][chan]->Draw();
    c1_1->Update();
    for(int y=0;y<8;y++) for(int x=0;x<4;x++) {c->cd(y*4+x+1); gPad->SetLogy(); hst[0][y*4+x]->Draw();}
    c->Update();
    for(int y=0;y<8;y++) for(int x=0;x<4;x++) {c_1->cd(y*4+x+1); gPad->SetLogy(); hst[1][y*4+x]->Draw();}
    c_1->Update();
    tr->Reset();
    evs=0;
    total_lost=0;
    for(int feb=0; feb<t->nclients; feb++)  { gts0[t->macs[feb][5]]->Set(0); }
    for(int feb=0; feb<t->nclients; feb++)  { gts1[t->macs[feb][5]]->Set(0); }
    c3->cd(1);
    //    hcprof->Draw("hist");
    c3->Update();

    hcprof->Reset(); 
    c4->cd();
    hcprof->Draw("hist");
    c4->Update();
    grevrate->Set(0); 
    c5->cd();
    grevrate->Draw("AL");
    grevrate->GetHistogram()->GetXaxis()->SetTitle("Poll Nr.");
    grevrate->GetHistogram()->GetYaxis()->SetTitle("Event rate, kHz");
    c5->Update();
    hevdisp->Reset(); 
    c6->cd();
    hevdisp->Draw("colz");
    c6->Update();

    //  evs_notfirst=0;
}

void All()
{
    for(int y=0;y<8;y++) for(int x=0;x<4;x++) { hst[BoardToMon][y*4+x]->Draw("same");}
}

void HVON()
{
    //for(int feb=0; feb<t->nclients; feb++)
    //{
    //SetDstMacByIndex(feb);
    t->dstmac[5]=0xff; //Broadcast
    t->SendCMD(t->dstmac,FEB_GEN_HVON,0x0000,buf);
    //}
}

void HVOF()
{
    //for(int feb=0; feb<t->nclients; feb++)
    //{
    //SetDstMacByIndex(feb);
    t->dstmac[5]=0xff; //Broadcast
    t->SendCMD(t->dstmac,FEB_GEN_HVOF,0x0000,buf);
    //}
}

float GetTriggerRate()
{
    float retval;
    t->SendCMD(t->macs[BoardToMon],FEB_GET_RATE,0,buf);
    retval=*((float*)(t->gpkt.Data));
    return retval;
}
void ThresholdScan(UShort_t start, UShort_t stop)
{
    UShort_t thr;
    Int_t i=0; 
    if(gr==0) gr=new TGraph();
    SetDstMacByIndex(BoardToMon);
    for( thr=start; thr<=stop; thr++)
    {
        SetThresholdDAC1(thr);
        SetThresholdDAC2(thr);
        gSystem->Sleep(2000); //to let FEB update rate
        gr->SetPoint(i,thr,GetTriggerRate());
        i++;
        c1->cd(); gr->Draw("AL");
        c1->Update();
        c1_1->cd(); gr->Draw("AL");
        c1_1->Update();
    }
}

void SetThresholdDAC1(UShort_t dac1)
{
    int offset=1107;
    for(int i=0; i<10;i++)
    { 
        if( (dac1 & 1)>0) ConfigSetBit(bufSCR,1144,offset+9-i,kTRUE);
        else ConfigSetBit(bufSCR,1144,offset+9-i,kFALSE);
        dac1= dac1 >> 1;
    }
    //UShort_t* pdac=(UShort_t*)(&bufSCR[3]);
    // printf("%4x",((*pdac)>>3)&0x3ff)
    //*pdac=*pdac & 0xE007; //clean bits of ADC1
    //*pdac=*pdac | ((dac1 << 3) & 0x1FF8);
    t->SendCMD(t->dstmac,FEB_WR_SCR,0x0000,bufSCR);
}

UShort_t GetThresholdDAC1()
{
    int offset=1107;
    UShort_t dac1=0;
    for(int i=0; i<10;i++)
    { 
        dac1= dac1 >> 1;
        if(ConfigGetBit(bufSCR,1144,offset+9-i)) dac1=dac1 | 0x0200;
    }
    return dac1;
}

void SetThresholdDAC2(UShort_t dac1)
{
    int offset=1107;
    for(int i=0; i<10;i++)
    { 
        if( (dac1 & 1)>0) ConfigSetBit(bufSCR,1144,offset+9-i,kTRUE);
        else ConfigSetBit(bufSCR,1144,offset+9-i,kFALSE);
        dac1= dac1 >> 1;
    }
    //UShort_t* pdac=(UShort_t*)(&bufSCR[3]);
    // printf("%4x",((*pdac)>>3)&0x3ff)
    //*pdac=*pdac & 0xE007; //clean bits of ADC1
    //*pdac=*pdac | ((dac1 << 3) & 0x1FF8);
    t->SendCMD(t->dstmac,FEB_WR_SCR,0x0000,bufSCR);
}


void GUI_UpdateThreshold()
{
    UShort_t dac1;
    dac1=fNumberEntry755->GetNumber();
    
    //	for(int feb=0; feb<t->nclients; feb++)
    //	{
    SetDstMacByIndex(BoardToMon);
    // t->dstmac[5]=0xff; //Broadcast
    SetThresholdDAC1(dac1);
    SetThresholdDAC2(dac1);
    //        }

    // assign threshold value to buffer variable as well
    thr_vals[BoardToMon] = dac1;

    if(GUI_VERBOSE)
    {
        std::cout << "Setting threshold of FEB " << BoardToMon << " to " << dac1 << std::endl;
        std::cout << "Selected tab ID: " << fTab683->GetCurrent() << std::endl;
        std::cout << "Active board ID: " << BoardToMon << std::endl;
        std::cout << "Active board MAC: " << int(t->dstmac[5]) << std::endl;
    }
}

void GUI_UpdateVCXO()
{
    t->VCXO=fNumberEntry75->GetNumber();
    t->SendCMD(t->macs[BoardToMon],FEB_SET_RECV,fNumberEntry75->GetNumber(),t->srcmac);    
}

void UpdateVCXOAllFEBs()
{
    for(int feb=0; feb<t->nclients; feb++)   t->SendCMD(t->macs[feb],FEB_SET_RECV,VCXO_Values[feb],t->srcmac);    
}

void UpdateBoardMonitor()
{
    // BoardToMon=fNumberEntry8869->GetNumber(); 
    char sttr[32];
    sprintf(sttr,"Mon FEB 0x%2x %d",t->macs[BoardToMon][5],t->macs[BoardToMon][5]);
    printf("Monitoring FEB mac5 0x%2x %d\n",t->macs[BoardToMon][5],t->macs[BoardToMon][5]);
    fLabel7->SetText(sttr); 
    //ResetHistos();
    // for(int y=0;y<8;y++) for(int x=0;x<4;x++) { hst[BoardToMon][y*4+x]->Reset();}

}

void FEBGUI()
{

    // main frame
    TGMainFrame *fMainFrame1314 = new TGMainFrame(gClient->GetRoot(),10,10,kMainFrame | kVerticalFrame);
    fMainFrame1314->SetName("fMainFrame1314");
    fMainFrame1314->SetLayoutBroken(kTRUE);

    // composite frame
    TGCompositeFrame *fMainFrame1560 = new TGCompositeFrame(fMainFrame1314,1329,789+100,kVerticalFrame);
    fMainFrame1560->SetName("fMainFrame1560");
    fMainFrame1560->SetLayoutBroken(kTRUE);

    // composite frame
    TGCompositeFrame *fMainFrame1241 = new TGCompositeFrame(fMainFrame1560,1329,789+100,kVerticalFrame);
    fMainFrame1241->SetName("fMainFrame1241");

    // vertical frame
    TGVerticalFrame *fVerticalFrame734 = new TGVerticalFrame(fMainFrame1241,1327,787+100,kVerticalFrame);
    fVerticalFrame734->SetName("fVerticalFrame734");

    // status bar
    Int_t parts[] = {15, 15, 15, 15, 15, 25};
    fStatusBar739 = new TGStatusBar(fVerticalFrame734,1327,18);
    fStatusBar739->SetName("fStatusBar739");
    fStatusBar739->SetParts(parts, 6);
    fVerticalFrame734->AddFrame(fStatusBar739, new TGLayoutHints(kLHintsBottom | kLHintsExpandX));



    // horizontal frame
    TGHorizontalFrame *fHorizontalFrame768 = new TGHorizontalFrame(fVerticalFrame734,1350,765+100,kHorizontalFrame);
    fHorizontalFrame768->SetName("fHorizontalFrame768");

    // "DAQ FEB controls" group frame
    TGGroupFrame *fGroupFrame679 = new TGGroupFrame(fHorizontalFrame768,"DAQ FEB controls");
    TGTextButton *fTextButton680 = new TGTextButton(fGroupFrame679,"Update Config");
    fTextButton680->SetTextJustify(36);
    fTextButton680->SetMargins(0,0,0,0);
    fTextButton680->SetWrapLength(-1);
    fTextButton680->Resize(123,22);
    fTextButton680->SetCommand("UpdateConfig()");
    fGroupFrame679->AddFrame(fTextButton680, new TGLayoutHints(kLHintsLeft | kLHintsCenterX | kLHintsTop | kLHintsExpandX,0,0,37,0));
    TGTextButton *fTextButton681 = new TGTextButton(fGroupFrame679,"Start DAQ");
    fTextButton681->SetTextJustify(36);
    fTextButton681->SetMargins(0,0,0,0);
    fTextButton681->SetWrapLength(-1);
    fTextButton681->Resize(123,22);
    fTextButton681->SetCommand("if(RunOn==0) StartDAQ();");
    fGroupFrame679->AddFrame(fTextButton681, new TGLayoutHints(kLHintsLeft | kLHintsCenterX | kLHintsTop | kLHintsExpandX,0,0,2,2));
    fNumberEntryTME= new TGNumberEntry(fGroupFrame679, (Double_t) 0,6,-1,(TGNumberFormat::EStyle) 5,(TGNumberFormat::EAttribute) 1,(TGNumberFormat::ELimit) 2,0,1e9);
    fGroupFrame679->AddFrame(fNumberEntryTME, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));


    TGTextButton *fTextButton682 = new TGTextButton(fGroupFrame679,"Stop DAQ");
    fTextButton682->SetTextJustify(36);
    fTextButton682->SetMargins(0,0,0,0);
    fTextButton682->SetWrapLength(-1);
    fTextButton682->Resize(123,22);
    fTextButton682->SetCommand("RunOn=0; StopDAQ(); QuitScan=true;");
    fGroupFrame679->AddFrame(fTextButton682, new TGLayoutHints(kLHintsLeft | kLHintsCenterX | kLHintsTop | kLHintsExpandX,0,0,2,2));

    TGTextButton *fTextButton788 = new TGTextButton(fGroupFrame679,"Reset Histos");
    fTextButton788->SetTextJustify(36);
    fTextButton788->SetMargins(0,0,0,0);
    fTextButton788->SetWrapLength(-1);
    fTextButton788->Resize(123,22);
    fGroupFrame679->AddFrame(fTextButton788, new TGLayoutHints(kLHintsLeft| kLHintsCenterX  | kLHintsTop | kLHintsExpandX,0,0,2,2));
    fTextButton788->SetCommand("Reset()");

    TGTextButton *fTextButton78 = new TGTextButton(fGroupFrame679,"SiPM HV ON");
    fTextButton78->SetTextJustify(36);
    fTextButton78->SetMargins(0,0,0,0);
    fTextButton78->SetWrapLength(-1);
    fTextButton78->Resize(123,22);
    fGroupFrame679->AddFrame(fTextButton78, new TGLayoutHints(kLHintsLeft| kLHintsCenterX  | kLHintsTop | kLHintsExpandX,0,0,2,2));
    fTextButton78->SetCommand("HVON()");

    TGTextButton *fTextButton88 = new TGTextButton(fGroupFrame679,"SiPM HV OFF");
    fTextButton88->SetTextJustify(36);
    fTextButton88->SetMargins(0,0,0,0);
    fTextButton88->SetWrapLength(-1);
    fTextButton88->Resize(123,22);
    fGroupFrame679->AddFrame(fTextButton88, new TGLayoutHints(kLHintsLeft| kLHintsCenterX  | kLHintsTop | kLHintsExpandX,0,0,2,2));
    fTextButton88->SetCommand("HVOF()");

    TGTextButton *fTextButton881 = new TGTextButton(fGroupFrame679,"Profile Test");
    fTextButton881->SetTextJustify(36);
    fTextButton881->SetMargins(0,0,0,0);
    fTextButton881->SetWrapLength(-1);
    fTextButton881->Resize(123,22);
    fGroupFrame679->AddFrame(fTextButton881, new TGLayoutHints(kLHintsLeft| kLHintsCenterX  | kLHintsTop | kLHintsExpandX,0,0,2,2));
    fTextButton881->SetCommand("MakeProfileTest()");


    fNumberEntry755 = new TGNumberEntry(fGroupFrame679, (Double_t) 250,6,-1,(TGNumberFormat::EStyle) 5,(TGNumberFormat::EAttribute) 1,(TGNumberFormat::ELimit) 2,0,1023);
    fGroupFrame679->AddFrame(fNumberEntry755, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,62,2));
    TGTextButton *fTextButton931 = new TGTextButton(fGroupFrame679,"Set Threshold DAC1");
    fTextButton931->SetTextJustify(36);
    fTextButton931->SetMargins(0,0,0,0);
    fTextButton931->SetWrapLength(-1);
    fTextButton931->Resize(123,22);
    fTextButton931->SetCommand("GUI_UpdateThreshold()");
    fGroupFrame679->AddFrame(fTextButton931, new TGLayoutHints(kLHintsLeft | kLHintsTop,0,0,2,2));


    fGroupFrame679->SetLayoutManager(new TGVerticalLayout(fGroupFrame679));
    fGroupFrame679->Resize(155,761);
    fHorizontalFrame768->AddFrame(fGroupFrame679, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandY,2,2,2,2));

    TGLabel *fLabel764 = new TGLabel(fGroupFrame679,"Select channel");
    fLabel764->SetTextJustify(36);
    fLabel764->SetMargins(0,0,0,0);
    fLabel764->SetWrapLength(-1);
    fGroupFrame679->AddFrame(fLabel764, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX,2,2,30,2));
    fNumberEntry886 = new TGNumberEntry(fGroupFrame679, (Double_t) 4,3,-1,(TGNumberFormat::EStyle) 5,(TGNumberFormat::EAttribute) 1,(TGNumberFormat::ELimit) 2,0,31);
    fGroupFrame679->AddFrame(fNumberEntry886, new TGLayoutHints(kLHintsExpandX | kLHintsCenterX ));
    fNumberEntry886->SetCommand("UpdateHisto()");



    fUpdateHisto = new TGCheckButton(fGroupFrame679,"Auto update histograms");
    fUpdateHisto->SetTextJustify(36);
    fUpdateHisto->SetMargins(0,0,0,0);
    fUpdateHisto->SetWrapLength(-1);
    fUpdateHisto->SetCommand("UpdateHisto()");
    fGroupFrame679->AddFrame(fUpdateHisto, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
    fUpdateHisto->SetOn();

    fUpdateVCXO = new TGCheckButton(fGroupFrame679,"Auto correct VCXOs");
    fUpdateVCXO->SetTextJustify(36);
    fUpdateVCXO->SetMargins(0,0,0,0);
    fUpdateVCXO->SetWrapLength(-1);
    //   fUpdateVCXO->SetCommand("UpdateHisto()");
    fGroupFrame679->AddFrame(fUpdateVCXO, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
    fUpdateVCXO->SetOn(0);
    fUpdateVCXO->SetEnabled(0);    

    TGCheckButton* fVerbose = new TGCheckButton(fGroupFrame679,"Verbose console output");
    fVerbose->SetTextJustify(36);
    fVerbose->SetMargins(0,0,0,0);
    fVerbose->SetWrapLength(-1);
    fVerbose->SetCommand("if(t->Verbose==1) t->Verbose=0; else t->Verbose=1;");
    fGroupFrame679->AddFrame(fVerbose, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
    //fVerbose->SetOff();


    /*  fLabel = new TGLabel(fGroupFrame679,"Trigger rate: 0 Hz");
        fLabel->SetTextJustify(36);
        fLabel->SetMargins(0,0,0,0);
        fLabel->SetWrapLength(-1);
        fGroupFrame679->AddFrame(fLabel, new TGLayoutHints(kLHintsLeft  | kLHintsExpandX,0,0,39,0));
     */

    fNumberEntry75 = new TGNumberEntry(fGroupFrame679, (Double_t) 500,6,-1,(TGNumberFormat::EStyle) 5,(TGNumberFormat::EAttribute) 1,(TGNumberFormat::ELimit) 2,0,1023);
    fGroupFrame679->AddFrame(fNumberEntry75, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,42,2));
    TGTextButton *fTextButton93 = new TGTextButton(fGroupFrame679,"Set VCXO correction");
    fTextButton93->SetTextJustify(36);
    fTextButton93->SetMargins(0,0,0,0);
    fTextButton93->SetWrapLength(-1);
    fTextButton93->Resize(123,22);
    fTextButton93->SetCommand("GUI_UpdateVCXO()");
    fGroupFrame679->AddFrame(fTextButton93, new TGLayoutHints(kLHintsLeft | kLHintsTop,0,0,2,2));




    TGTextButton *fTextButton111 = new TGTextButton(fGroupFrame679,"Save data tree");
    fTextButton111->SetTextJustify(36);
    fTextButton111->SetMargins(0,0,0,0);
    fTextButton111->SetWrapLength(-1);
    fTextButton111->Resize(123,22);
    fGroupFrame679->AddFrame(fTextButton111, new TGLayoutHints(kLHintsLeft| kLHintsCenterX  | kLHintsTop | kLHintsExpandX,0,0,2,2));
    // fTextButton111->SetCommand("tr->SaveAs(\"mppc.root\");");
    // save mppc data to file as well as hardware settings
    fTextButton111->SetCommand("SaveToFile(\"mppc.root\");");

    fLabel7 = new TGLabel(fGroupFrame679,"0xHH");
    fLabel7->SetTextJustify(36);
    fLabel7->SetMargins(0,0,0,0);
    fLabel7->SetWrapLength(-1);
    fGroupFrame679->AddFrame(fLabel7, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX,2,2,39,2));

    TGLabel *fLabel769 = new TGLabel(fGroupFrame679,"Select FEB");
    fLabel769->SetTextJustify(36);
    fLabel769->SetMargins(0,0,0,0);
    fLabel769->SetWrapLength(-1);
    fGroupFrame679->AddFrame(fLabel769, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX,2,2,30,2));
    fNumberEntry8869 = new TGNumberEntry(fGroupFrame679, (Double_t) 0,3,-1,(TGNumberFormat::EStyle) 5,(TGNumberFormat::EAttribute) 1,(TGNumberFormat::ELimit) 3,0,255);
    fGroupFrame679->AddFrame(fNumberEntry8869, new TGLayoutHints(kLHintsExpandX | kLHintsCenterX ));

    fNumberEntry8869->Connect("ValueSet(Long_t)", 0, 0,  "UpdateBoardMonitor()");
    // Diable the ability to modify the value.
    fNumberEntry8869->SetState(kFALSE);

    TGTextButton *fTextButton1188 = new TGTextButton(fGroupFrame679,"Rescan network");
    fTextButton1188->SetTextJustify(36);
    fTextButton1188->SetMargins(0,0,0,0);
    fTextButton1188->SetWrapLength(-1);
    fTextButton1188->Resize(123,22);
    fGroupFrame679->AddFrame(fTextButton1188, new TGLayoutHints(kLHintsLeft| kLHintsCenterX  | kLHintsTop | kLHintsExpandX,0,0,2,2));
    fTextButton1188->SetCommand("RescanNet()");

    //**************************************************************************
    // My editing:
    // Add a button to bring up the control application for other components,
    // such as the poswer unit and the function generator.
    TGTextButton *fTextButton1189 = new TGTextButton(fGroupFrame679,
                                                     "Slow Control");
    fTextButton1189->SetTextJustify(36);
    fTextButton1189->SetMargins(0,0,0,0);
    fTextButton1189->SetWrapLength(-1);
    fTextButton1189->Resize(123,22);
    fGroupFrame679->AddFrame(fTextButton1189, new TGLayoutHints(kLHintsLeft |
                             kLHintsCenterX  | kLHintsTop |
                             kLHintsExpandX,0,0,2,2));
    fTextButton1189->SetCommand("ControlApp()");
    // End of my editing.
    //**************************************************************************



    // tab widget
    fTab683 = new TGTab(fHorizontalFrame768,1187,761+100);
    //**************************************************************************
    // My code: connect to the slot that checks which tab is selected and 
    //          assigns the FEB accordingly.
    fTab683->SetCommand("SelectBoard()");
    // End of my code.
    //**************************************************************************

    // container of "Configuration"
    TGCompositeFrame *fCompositeFrame686;
    fCompositeFrame686 = fTab683->AddTab("Configuration");
    fCompositeFrame686->SetLayoutManager(new TGHorizontalLayout(fCompositeFrame686));
    char str[32];

    TGVButtonGroup* fButtonGroup2=new TGVButtonGroup(fCompositeFrame686,"Enable Amplifier");
    for(int i=0;i<32;i++)
    {
        sprintf(str,"ch%d",i);
        fChanEnaAmp[0][i] = new TGCheckButton(fButtonGroup2,str);
        fChanEnaAmp[0][i]->SetTextJustify(36);
        fChanEnaAmp[0][i]->SetMargins(0,0,0,0);
        fChanEnaAmp[0][i]->SetWrapLength(-1);
        fChanEnaAmp[0][i]->SetCommand("SendConfig()");
    }
    fChanEnaAmp[0][32] = new TGCheckButton(fButtonGroup2,"All");
    fChanEnaAmp[0][32]->SetTextJustify(36);
    fChanEnaAmp[0][32]->SetMargins(0,0,0,0);
    fChanEnaAmp[0][32]->SetWrapLength(-1);
    fChanEnaAmp[0][32]->SetCommand("SendAllChecked()");
    fChanEnaAmp[0][33] = new TGCheckButton(fButtonGroup2,"None");
    fChanEnaAmp[0][33]->SetTextJustify(36);
    fChanEnaAmp[0][33]->SetMargins(0,0,0,0);
    fChanEnaAmp[0][33]->SetWrapLength(-1);
    fChanEnaAmp[0][33]->SetCommand("SendAllUnChecked()");

    fCompositeFrame686->AddFrame(fButtonGroup2, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
    fButtonGroup2->Show();

    TGVButtonGroup* fButtonGroup3=new TGVButtonGroup(fCompositeFrame686,"Enable Trigger");
    for(int i=0;i<32;i++)
    {
        sprintf(str,"ch%d",i);
        fChanEnaTrig[0][i] = new TGCheckButton(fButtonGroup3,str);
        fChanEnaTrig[0][i]->SetTextJustify(36);
        fChanEnaTrig[0][i]->SetMargins(0,0,0,0);
        fChanEnaTrig[0][i]->SetWrapLength(-1);
        fChanEnaTrig[0][i]->SetCommand("SendConfig()");
    }
    fChanEnaTrig[0][32] = new TGCheckButton(fButtonGroup3,"OR32");
    fChanEnaTrig[0][32]->SetTextJustify(36);
    fChanEnaTrig[0][32]->SetMargins(0,0,0,0);
    fChanEnaTrig[0][32]->SetWrapLength(-1);
    fChanEnaTrig[0][32]->SetCommand("SendConfig()");

    fCompositeFrame686->AddFrame(fButtonGroup3, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
    fButtonGroup3->Show();


    TGVButtonGroup* fButtonGroup1=new TGVButtonGroup(fCompositeFrame686,"Probe register");
    for(int i=0;i<32;i++)
    {
        sprintf(str,"ch%d",i);
        fChanProbe[0][i] = new TGRadioButton(fButtonGroup1,str);
        fChanProbe[0][i]->SetTextJustify(36);
        fChanProbe[0][i]->SetMargins(0,0,0,0);
        fChanProbe[0][i]->SetWrapLength(-1);
        fChanProbe[0][i]->SetCommand("SendConfig()");
    }
    fChanProbe[0][32] = new TGRadioButton(fButtonGroup1,"None");
    fChanProbe[0][32]->SetTextJustify(36);
    fChanProbe[0][32]->SetMargins(0,0,0,0);
    fChanProbe[0][32]->SetWrapLength(-1);
    fChanProbe[0][32]->SetCommand("SendConfig()");
    fCompositeFrame686->AddFrame(fButtonGroup1, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
    fButtonGroup1->SetRadioButtonExclusive(kTRUE);
    fButtonGroup1->Show();
    fChanProbe[0][4]->SetOn();

    // TGGroupFrame* fGainsGroup = new TGGroupFrame(
    TGGroupFrame* fGains=new TGGroupFrame(fCompositeFrame686,"HG preamp gain/bias");
    //fGains->SetLayoutManager(new TGVerticalLayout(fGains));
    fGains->SetLayoutManager(new TGMatrixLayout(fGains, 32, 3, 0, kLHintsLeft | kLHintsTop));
    for(int i=0;i<32;i++)
    {
        sprintf(str," CH %d",i);
        fChanGain[0][i] = new TGNumberEntry(fGains, (Double_t) i,2,-1,(TGNumberFormat::EStyle) 0,(TGNumberFormat::EAttribute) 1,(TGNumberFormat::ELimit) 2,0,64);
        fChanGain[0][i]->Connect("ValueSet(Long_t)", 0, 0,  "SendConfig()");
        fChanGain[0][i]->SetHeight(20);
        fChanBias[0][i] = new TGNumberEntry(fGains, (Double_t) i,3,-1,(TGNumberFormat::EStyle) 0,(TGNumberFormat::EAttribute) 1,(TGNumberFormat::ELimit) 2,0,256);
        fChanBias[0][i]->Connect("ValueSet(Long_t)", 0, 0,  "SendConfig()");
        fChanBias[0][i]->SetHeight(20);
        fGains->AddFrame(new TGLabel(fGains,str));
        fGains->AddFrame(fChanGain[0][i]);
        fGains->AddFrame(fChanBias[0][i]);

    }
    fCompositeFrame686->AddFrame(fGains, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));

    // container of "All histos"
    TGCompositeFrame *fCompositeFrame720;
    fCompositeFrame720 = fTab683->AddTab("All histos");
    fCompositeFrame720->SetLayoutManager(new TGVerticalLayout(fCompositeFrame720));

    // embedded canvas
    TRootEmbeddedCanvas *fRootEmbeddedCanvas721 = new TRootEmbeddedCanvas(0,fCompositeFrame720,1179,732+100);
    Int_t wfRootEmbeddedCanvas721 = fRootEmbeddedCanvas721->GetCanvasWindowId();
    c = new TCanvas("c", 10, 10, wfRootEmbeddedCanvas721);    c->Divide(4,8);

    fRootEmbeddedCanvas721->AdoptCanvas(c);
    fCompositeFrame720->AddFrame(fRootEmbeddedCanvas721, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX | kLHintsExpandY,2,2,2,2));


    // container of "One channel"
    TGCompositeFrame *fCompositeFrame735;
    fCompositeFrame735 = fTab683->AddTab("One channel");
    fCompositeFrame735->SetLayoutManager(new TGVerticalLayout(fCompositeFrame735));

    // embedded canvas
    TRootEmbeddedCanvas *fRootEmbeddedCanvas736 = new TRootEmbeddedCanvas(0,fCompositeFrame735,1179,732+100);
    Int_t wfRootEmbeddedCanvas736 = fRootEmbeddedCanvas736->GetCanvasWindowId();
    c1 = new TCanvas("c1", 10, 10, wfRootEmbeddedCanvas736);
    fRootEmbeddedCanvas736->AdoptCanvas(c1);
    fCompositeFrame735->AddFrame(fRootEmbeddedCanvas736, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX | kLHintsExpandY,2,2,2,2));

    // container of "Timing data"
    TGCompositeFrame *fCompositeFrame7351;
    fCompositeFrame7351 = fTab683->AddTab("Timing data");
    fCompositeFrame7351->SetLayoutManager(new TGVerticalLayout(fCompositeFrame7351));

    // embedded canvas
    TRootEmbeddedCanvas *fRootEmbeddedCanvas7361 = new TRootEmbeddedCanvas(0,fCompositeFrame7351,1179,732+100);
    Int_t wfRootEmbeddedCanvas7361 = fRootEmbeddedCanvas7361->GetCanvasWindowId();
    c3 = new TCanvas("c3", 10, 10, wfRootEmbeddedCanvas7361);
    fRootEmbeddedCanvas7361->AdoptCanvas(c3);
    fCompositeFrame7351->AddFrame(fRootEmbeddedCanvas7361, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX | kLHintsExpandY,2,2,2,2));
    c3->Divide(1,2);
    c3->cd(1)->SetGridx(1);
    c3->cd(1)->SetGridy(1);
    c3->cd(2)->SetGridx(1);
    c3->cd(2)->SetGridy(1);

    // container of "TChannel profile"
    TGCompositeFrame *fCompositeFrame7352;
    fCompositeFrame7352 = fTab683->AddTab("Channel profile");
    fCompositeFrame7352->SetLayoutManager(new TGVerticalLayout(fCompositeFrame7352));

    // embedded canvas
    TRootEmbeddedCanvas *fRootEmbeddedCanvas7362 = new TRootEmbeddedCanvas(0,fCompositeFrame7352,1179,732+100);
    Int_t wfRootEmbeddedCanvas7362 = fRootEmbeddedCanvas7362->GetCanvasWindowId();
    c4 = new TCanvas("c4", 10, 10, wfRootEmbeddedCanvas7362);
    fRootEmbeddedCanvas7362->AdoptCanvas(c4);
    fCompositeFrame7352->AddFrame(fRootEmbeddedCanvas7362, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX | kLHintsExpandY,2,2,2,2));
    c4->SetGridx(1);
    c4->SetGridy(1);

    // container of "Rate history"
    TGCompositeFrame *fCompositeFrame73521;
    fCompositeFrame73521 = fTab683->AddTab("Event rate");
    fCompositeFrame73521->SetLayoutManager(new TGVerticalLayout(fCompositeFrame73521));

    // embedded canvas
    TRootEmbeddedCanvas *fRootEmbeddedCanvas73621 = new TRootEmbeddedCanvas(0,fCompositeFrame73521,1179,732+100);
    Int_t wfRootEmbeddedCanvas73621 = fRootEmbeddedCanvas73621->GetCanvasWindowId();
    c5 = new TCanvas("c5", 10, 10, wfRootEmbeddedCanvas73621);
    fRootEmbeddedCanvas73621->AdoptCanvas(c5);
    fCompositeFrame73521->AddFrame(fRootEmbeddedCanvas73621, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX | kLHintsExpandY,2,2,2,2));
    c5->SetGridx(1);
    c5->SetGridy(1);

    // container of "Event display"
    TGCompositeFrame *fCompositeFrame73522;
    fCompositeFrame73522 = fTab683->AddTab("Event display");
    fCompositeFrame73522->SetLayoutManager(new TGVerticalLayout(fCompositeFrame73522));

    // embedded canvas
    TRootEmbeddedCanvas *fRootEmbeddedCanvas73622 = new TRootEmbeddedCanvas(0,fCompositeFrame73522,1179,732+100);
    Int_t wfRootEmbeddedCanvas73622 = fRootEmbeddedCanvas73622->GetCanvasWindowId();
    c6 = new TCanvas("c6", 10, 10, wfRootEmbeddedCanvas73622);
    fRootEmbeddedCanvas73622->AdoptCanvas(c6);
    fCompositeFrame73522->AddFrame(fRootEmbeddedCanvas73622, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX | kLHintsExpandY,2,2,2,2));


    // Adding my own tabs at the end
    //**************************************************************************
    // My modification *********************************************************
    // container of "Configuration" for another board
    TGCompositeFrame *fCompositeFrame6862;
    fCompositeFrame6862 = fTab683->AddTab("Configuration 2");
    fCompositeFrame6862->SetLayoutManager(new TGHorizontalLayout(fCompositeFrame6862));
    char str2[32];

    TGVButtonGroup* fButtonGroup22=new TGVButtonGroup(fCompositeFrame6862,"Enable Amplifier");
    for(int i=0;i<32;i++)
    {
        sprintf(str2,"ch%d",i);
        fChanEnaAmp[1][i] = new TGCheckButton(fButtonGroup22,str2);
        fChanEnaAmp[1][i]->SetTextJustify(36);
        fChanEnaAmp[1][i]->SetMargins(0,0,0,0);
        fChanEnaAmp[1][i]->SetWrapLength(-1);
        fChanEnaAmp[1][i]->SetCommand("SendConfig()");
    }
    fChanEnaAmp[1][32] = new TGCheckButton(fButtonGroup22,"All");
    fChanEnaAmp[1][32]->SetTextJustify(36);
    fChanEnaAmp[1][32]->SetMargins(0,0,0,0);
    fChanEnaAmp[1][32]->SetWrapLength(-1);
    fChanEnaAmp[1][32]->SetCommand("SendAllChecked()");
    fChanEnaAmp[1][33] = new TGCheckButton(fButtonGroup22,"None");
    fChanEnaAmp[1][33]->SetTextJustify(36);
    fChanEnaAmp[1][33]->SetMargins(0,0,0,0);
    fChanEnaAmp[1][33]->SetWrapLength(-1);
    fChanEnaAmp[1][33]->SetCommand("SendAllUnChecked()");

    fCompositeFrame6862->AddFrame(fButtonGroup22, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
    fButtonGroup22->Show();

    TGVButtonGroup* fButtonGroup32=new TGVButtonGroup(fCompositeFrame6862,"Enable Trigger");
    for(int i=0;i<32;i++)
    {
        sprintf(str2,"ch%d",i);
        fChanEnaTrig[1][i] = new TGCheckButton(fButtonGroup32,str2);
        fChanEnaTrig[1][i]->SetTextJustify(36);
        fChanEnaTrig[1][i]->SetMargins(0,0,0,0);
        fChanEnaTrig[1][i]->SetWrapLength(-1);
        fChanEnaTrig[1][i]->SetCommand("SendConfig()");
    }
    fChanEnaTrig[1][32] = new TGCheckButton(fButtonGroup32,"OR32");
    fChanEnaTrig[1][32]->SetTextJustify(36);
    fChanEnaTrig[1][32]->SetMargins(0,0,0,0);
    fChanEnaTrig[1][32]->SetWrapLength(-1);
    fChanEnaTrig[1][32]->SetCommand("SendConfig()");

    fCompositeFrame6862->AddFrame(fButtonGroup32, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
    fButtonGroup32->Show();


    TGVButtonGroup* fButtonGroup12=new TGVButtonGroup(fCompositeFrame6862,"Probe register");
    for(int i=0;i<32;i++)
    {
        sprintf(str2,"ch%d",i);
        fChanProbe[1][i] = new TGRadioButton(fButtonGroup12,str2);
        fChanProbe[1][i]->SetTextJustify(36);
        fChanProbe[1][i]->SetMargins(0,0,0,0);
        fChanProbe[1][i]->SetWrapLength(-1);
        fChanProbe[1][i]->SetCommand("SendConfig()");
    }
    fChanProbe[1][32] = new TGRadioButton(fButtonGroup12,"None");
    fChanProbe[1][32]->SetTextJustify(36);
    fChanProbe[1][32]->SetMargins(0,0,0,0);
    fChanProbe[1][32]->SetWrapLength(-1);
    fChanProbe[1][32]->SetCommand("SendConfig()");
    fCompositeFrame6862->AddFrame(fButtonGroup12, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
    fButtonGroup12->SetRadioButtonExclusive(kTRUE);
    fButtonGroup12->Show();
    fChanProbe[1][4]->SetOn();

    // TGGroupFrame* fGainsGroup = new TGGroupFrame(
    TGGroupFrame* fGains2=new TGGroupFrame(fCompositeFrame6862,"HG preamp gain/bias");
    //fGains2->SetLayoutManager(new TGVerticalLayout(fGains2));
    fGains2->SetLayoutManager(new TGMatrixLayout(fGains2, 32, 3, 0, kLHintsLeft | kLHintsTop));
    for(int i=0;i<32;i++)
    {
        sprintf(str2," CH %d",i);
        fChanGain[1][i] = new TGNumberEntry(fGains2, (Double_t) i,2,-1,(TGNumberFormat::EStyle) 0,(TGNumberFormat::EAttribute) 1,(TGNumberFormat::ELimit) 2,0,64);
        fChanGain[1][i]->Connect("ValueSet(Long_t)", 0, 0,  "SendConfig()");
        fChanGain[1][i]->SetHeight(20);
        fChanBias[1][i] = new TGNumberEntry(fGains2, (Double_t) i,3,-1,(TGNumberFormat::EStyle) 0,(TGNumberFormat::EAttribute) 1,(TGNumberFormat::ELimit) 2,0,256);
        fChanBias[1][i]->Connect("ValueSet(Long_t)", 0, 0,  "SendConfig()");
        fChanBias[1][i]->SetHeight(20);
        fGains2->AddFrame(new TGLabel(fGains2,str2));
        fGains2->AddFrame(fChanGain[1][i]);
        fGains2->AddFrame(fChanBias[1][i]);

    }
    fCompositeFrame6862->AddFrame(fGains2, new TGLayoutHints(kLHintsLeft | kLHintsTop,2,2,2,2));
    // End of my modification **************************************************
    //**************************************************************************

    //**************************************************************************
    // My modification *********************************************************
    // container of "All histos"
    TGCompositeFrame *fCompositeFrame7202;
    fCompositeFrame7202 = fTab683->AddTab("All histos 2");
    fCompositeFrame7202->SetLayoutManager(new TGVerticalLayout(fCompositeFrame7202));

    // embedded canvas
    TRootEmbeddedCanvas *fRootEmbeddedCanvas7212 = new TRootEmbeddedCanvas(0,fCompositeFrame7202,1179,732+100);
    Int_t wfRootEmbeddedCanvas7212 = fRootEmbeddedCanvas7212->GetCanvasWindowId();
    c_1 = new TCanvas("c_1", 10, 10, wfRootEmbeddedCanvas7212);    c_1->Divide(4,8);

    fRootEmbeddedCanvas7212->AdoptCanvas(c_1);
    fCompositeFrame7202->AddFrame(fRootEmbeddedCanvas7212, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX | kLHintsExpandY,2,2,2,2));

    // container of "One channel"
    TGCompositeFrame *fCompositeFrame735_1;
    fCompositeFrame735_1 = fTab683->AddTab("One channel 2");
    fCompositeFrame735_1->SetLayoutManager(new TGVerticalLayout(fCompositeFrame735_1));

    // embedded canvas
    TRootEmbeddedCanvas *fRootEmbeddedCanvas736_1 = new TRootEmbeddedCanvas(0,fCompositeFrame735_1,1179,732+100);
    Int_t wfRootEmbeddedCanvas736_1 = fRootEmbeddedCanvas736_1->GetCanvasWindowId();
    c1_1 = new TCanvas("c1_1", 10, 10, wfRootEmbeddedCanvas736_1);
    fRootEmbeddedCanvas736_1->AdoptCanvas(c1_1);
    fCompositeFrame735_1->AddFrame(fRootEmbeddedCanvas736_1, new TGLayoutHints(kLHintsLeft | kLHintsTop | kLHintsExpandX | kLHintsExpandY,2,2,2,2));
    
    // End of my modification **************************************************
    //**************************************************************************

    // If only one board is detected, disable tabs reserved for additional ones.
    if(nboard_detected == 1)
        for(int tab_id = 7; tab_id < fTab683->GetNumberOfTabs(); tab_id++)
            fTab683->SetEnabled(tab_id, kFALSE);

    fTab683->SetTab(2);

    fTab683->Resize(fTab683->GetDefaultSize());
    fHorizontalFrame768->AddFrame(fTab683, new TGLayoutHints(kLHintsRight | kLHintsTop | kLHintsExpandX | kLHintsExpandY,2,2,2,2));

    fVerticalFrame734->AddFrame(fHorizontalFrame768, new TGLayoutHints(kLHintsTop | kLHintsExpandX | kLHintsExpandY,2,2,2,2));

    fMainFrame1241->AddFrame(fVerticalFrame734, new TGLayoutHints(kLHintsExpandX | kLHintsExpandY,1,1,1,1));

    fMainFrame1560->AddFrame(fMainFrame1241, new TGLayoutHints(kLHintsExpandX | kLHintsExpandY));
    fMainFrame1241->MoveResize(0,0,1329,789+100);

    fMainFrame1314->AddFrame(fMainFrame1560, new TGLayoutHints(kLHintsExpandX | kLHintsExpandY));
    fMainFrame1560->MoveResize(0,0,1329,789+100);

    fMainFrame1314->SetMWMHints(kMWMDecorAll,
            kMWMFuncAll,
            kMWMInputModeless);
    fMainFrame1314->MapSubwindows();

    fMainFrame1314->Resize(fMainFrame1314->GetDefaultSize());
    fMainFrame1314->MapWindow();
    fMainFrame1314->Resize(1329,789+100);
}  

uint8_t getCRC(uint8_t message[], uint32_t length)
{
    uint32_t i, j;
    uint8_t crc = 0;

    for (i = 0; i < length; i++)
    {
        crc ^= message[i];
        for (j = 0; j < 8; j++)
        {
            if (crc & 1)
                crc ^=  0x91; //CRC7_POLY
            crc >>= 1;
        }
    }
    return crc;
}

std::string get_current_dir() {
   char buff[FILENAME_MAX]; //create string buffer to hold path
   char* tmpstr = getcwd( buff, FILENAME_MAX );
   std::string current_working_dir(buff);
   return current_working_dir;
}

int FW_ptr=0;
uint8_t fwbuf[1024*1024]; //Firmware buffer
uint8_t crc7;

void ReceiveFW(int truncat)  // hook called by libFEBDTP when event is received
{
    for(int j=0;j<1024; j++) {
        if(t->Verbose) { printf("%02x ",t->gpkt.Data[j]);     if(j%16==15) printf("\n"); }
        fwbuf[FW_ptr+j]=t->gpkt.Data[j];
    }
    FW_ptr+=1024;
}

bool DumpFW(uint32_t startaddr=0, uint16_t blocks=1)
{
    bool retval=1;
    // memset(fwbuf,1024*1024,00);
    buf[0]=startaddr & 0x000000ff;
    buf[1]=(startaddr & 0x0000ff00)>>8;
    buf[2]=(startaddr & 0x00ff0000)>>16;
    buf[3]=(blocks & 0x00FF);
    buf[4]=(blocks & 0xFF00) >>8;
    t->setPacketHandler(&ReceiveFW);
    FW_ptr=startaddr;
    t->SendCMD(t->dstmac,FEB_RD_FW,00,buf);//==0) //retval=0;
    t->setPacketHandler(&FillHistos);
    crc7=getCRC(&(fwbuf[startaddr]),blocks*1024);
    printf("DumpFW: Received %d bytes at 0x%08x in Flash ( 0x%08x in CPU address space)",blocks*1024,startaddr,startaddr+0x14000000);
    if(crc7==t->gpkt.REG)  printf("CRC check OK (%02x).\n",crc7);
    else  { printf("CRC check NOT OK!! received CRC=%02x, locally calculated on Host=%02x!\n",crc7,t->gpkt.REG); retval=0;}
    if(retval==0) printf("Error in DumpFW!!\n");
    return retval;
}

void RateScanSummary(std::string srcfpn, int dateID, int timeID, int curFeb, int curCh, float thr, int drsNEvt)
{
    // open or create the summary file
    char* outfpn = Form("rate_scan/summary/%d_%d_dark_rate_summary.root", dateID, timeID);
    TFile toutf = TFile(outfpn, "update");
    TTree* tr_rate;
    
    // assign tree branches
    Int_t board;
    Int_t channel;
    Int_t nevtSet;
    Float_t DAC;
    Bool_t isTrigger;
    Int_t preampGain;
    Int_t channelBias;
    Int_t nrate;
    Float_t meanRate;
    Float_t meanRate_sw; // software mean rate
    std::vector<float> rates;

    // If the tree exists, open it. Otherwise, create it.
    // Ref: https://root-forum.cern.ch/t/appending-to-a-ttree-or-creating-if-it-does-not-exist/17974
    tr_rate = (TTree*)toutf.Get("tr_rate");
    if(!tr_rate)
    {
        tr_rate = new TTree("tr_rate", "ntuple for rate scan results");
        tr_rate->Branch("mac5", &mac5, "mac5/b");
        tr_rate->Branch("board", &board, "board/I");
        tr_rate->Branch("channel", &channel, "channel/I");
        tr_rate->Branch("nevtSet", &nevtSet, "nevtSet/I");
        tr_rate->Branch("DAC", &DAC, "DAC/F");
        tr_rate->Branch("isTrigger", &isTrigger, "isTrigger/O");
        tr_rate->Branch("preampGain", &preampGain, "preampGain/I");
        tr_rate->Branch("channelBias", &channelBias, "channelBias/I");
        tr_rate->Branch("nrate", &nrate, "nrate/I");
        tr_rate->Branch("meanRate", &meanRate, "meanRate/F");
        tr_rate->Branch("meanRate_sw", &meanRate_sw, "meanRate_sw/F");
        // tr_rate->Branch("rates", &rates);
    }
    else
    {
        tr_rate->GetBranch("mac5")->SetAddress(&mac5);
        tr_rate->GetBranch("board")->SetAddress(&board);
        tr_rate->GetBranch("channel")->SetAddress(&channel);
        tr_rate->GetBranch("nevtSet")->SetAddress(&nevtSet);
        tr_rate->GetBranch("DAC")->SetAddress(&DAC);
        tr_rate->GetBranch("isTrigger")->SetAddress(&isTrigger);
        tr_rate->GetBranch("preampGain")->SetAddress(&preampGain);
        tr_rate->GetBranch("channelBias")->SetAddress(&channelBias);
        tr_rate->GetBranch("nrate")->SetAddress(&nrate);
        tr_rate->GetBranch("meanRate")->SetAddress(&meanRate);
        tr_rate->GetBranch("meanRate_sw")->SetAddress(&meanRate_sw);
        // tr_rate->GetBranch("rates")->SetAddress(rates);
    }
    

    // fill the rate tree
    board = curFeb;
    channel = curCh;
    nevtSet = drsNEvt;
    DAC = thr;
    isTrigger = fChanEnaTrig[curFeb][curCh]->IsOn();
    preampGain = fChanGain[curFeb][curCh]->GetNumber();
    channelBias = fChanBias[curFeb][curCh]->GetNumber();
    // calculate the mean trigger rate
    TFile tinf = TFile(srcfpn.c_str());
    TTree* mppc = (TTree*)tinf.Get("mppc");
    long t_start = 0;
    long t_end = 0;
    for(int i = 0; i < mppc->GetEntries(); i++)
    {
        mppc->GetEntry(i);
        float rate = mppc->GetLeaf("trig_rate")->GetValue();
        if(rate > 0) rates.push_back(rate);

        if(i == 0) t_start = mppc->GetLeaf("ns_epoch")->GetValue();
        if(i == (mppc->GetEntries()-1))
            t_end = mppc->GetLeaf("ns_epoch")->GetValue();
    }
    if(rates.size()) meanRate = 1e3*TMath::Mean(rates.begin(), rates.end());
    else meanRate = 0;
    nrate = rates.size();
    if(t_end > t_start) meanRate_sw = mppc->GetEntries()/((t_end-t_start)/1e9);
    else meanRate_sw = 0;
    tr_rate->Fill();

    toutf.cd();
    tr_rate->Write("", TObject::kOverwrite);
    toutf.Close();
}

void ProcessMessage(std::string msg)
{
    // Initialize QuitScan such that scan loops are executed with certainty.
    QuitScan = false;

    // local utility declaration
    Document document;
    document.Parse(msg.c_str());
    // clean up the parameter containers
    scanFeb1gains.clear();
    scanFeb2gains.clear();
    std::vector<int> drsFebs;
    std::vector<int> drsChs;
    int psNEvt = 0;
    int drsNEvt = 0;
    float biasVoltage = -1;
    float temperature = -1;
    std::string out_fdr = "";
    std::string boardID = "";

    // make sure output directory exists
    gROOT->ProcessLine(".! mkdir -p output_data");
    gROOT->ProcessLine(".! mkdir -p rate_scan/raw_data");
    gROOT->ProcessLine(".! mkdir -p rate_scan/summary");

    // For useage examples, see
    // https://rapidjson.org/md_doc_tutorial.html
    for(Value::ConstMemberIterator itr = document.MemberBegin(); itr != document.MemberEnd(); ++itr)
    {
        if(std::string(itr->name.GetString()) == "feb1gain")
        {
            float from, to, step;
            from = std::stoi(itr->value["from"].GetString());
            to = std::stoi(itr->value["to"].GetString());
            step = std::stoi(itr->value["step"].GetString());
            for(float g = from; g <= to; g += step)
                scanFeb1gains.push_back(g);
        }
        if(std::string(itr->name.GetString()) == "feb2gain")
        {
            float from, to, step;
            from = std::stoi(itr->value["from"].GetString());
            to = std::stoi(itr->value["to"].GetString());
            step = std::stoi(itr->value["step"].GetString());
            for(float g = from; g <= to; g += step)
                scanFeb2gains.push_back(g);
        }
    }

    //***** Voltage Scan *****
    // Grab the number of events for parameter scan.
    if(document.HasMember("number of events"))
        psNEvt = std::stoi(document["number of events"].GetString());
    if(document.HasMember("boardID"))
        boardID = document["boardID"].GetString();
    //***** Start DAQ *****
    // For a first implementation, set gains on both boards according to the
    // feb1gains array.
    // if(!document.HasMember("dark rate scan"))
    // {
    //     for(unsigned int gIdx = 0; gIdx < scanFeb1gains.size(); gIdx++)
    //     {
    //         int curGain = scanFeb1gains[gIdx];
    //         std::cout << "Processing gain " << curGain << std::endl;
    //         for(unsigned int j = 0; j < 32; j++)
    //         {
    //             fChanGain[0][j]->SetNumber(curGain);
    //             fChanGain[1][j]->SetNumber(curGain);
    //         }
    //         // apply the settings
    //         SendConfig2All();
    //         // clear the data container
    //         Reset();
    //         // Start taking data!
    //         slowerBoard = -1;
    //         if(RunOn == 0) StartDAQ(psNEvt);
    //         // save to disk
    //         TDatime tdt;
    //         tr->SaveAs(Form("%d_mppc_gain%d.root", tdt.GetDate(), curGain));
    //     }
    // }

    // Read the bias voltage and the temperature
    if(document.HasMember("bias_voltage"))
        biasVoltage = std::stof(document["bias_voltage"].GetString());
    if(document.HasMember("temperature"))
        temperature = document["temperature"].GetFloat();
    if(document.HasMember("led_Vpp"))
        led_Vpp = document["led_Vpp"].GetFloat();

    // get date and time as the file group ID
    TDatime tdt;
    int dateID = tdt.GetDate();
    int timeID = tdt.GetTime();
    //***** Handle voltage scan scenario *****
    float vol = 58;
    float temp = 20;
    float gain = -1;
    float gain2 = -1;
    float threshold_dac = -1;
    int msg_time = -1;
    if(document.HasMember("vol")) vol = document["vol"].GetFloat();
    if(document.HasMember("temp")) temp = std::stof(document["temp"].GetString());
    if(document.HasMember("gain")) gain = document["gain"].GetFloat();
    if(document.HasMember("gain2")) gain2 = document["gain2"].GetFloat();
    if(document.HasMember("dac")) threshold_dac = document["dac"].GetFloat();
    if(document.HasMember("time")) msg_time = std::stoi(document["time"].GetString());
    // This means DAQ on!
    if(document.HasMember("parameter scan"))
    {
        // First, signal slow control I am busy.
        const char json[] = " { \"daq status\" : \"busy\" } ";
        SendMsg2SlowCtrl(json);

        ////////////////////////////////////////////////////////////////////////
        // set up the threshold
        thr_vals[0] = threshold_dac;
        thr_vals[1] = threshold_dac;

        // remember the current tab
        int curTabId = fTab683->GetCurrent();
        // change values on the GUI and send configuration to FEB
        int activeFeb = BoardToMon;
        for(int bid = 0; bid < t->nclients; bid++)
        {
            BoardToMon = bid;
            fNumberEntry755->SetNumber(threshold_dac);
            fTab683->SetTab(bid);
            SelectBoard();
            SetDstMacByIndex(bid);
            GUI_UpdateThreshold();
        }

        // restore settings
        BoardToMon = activeFeb;
        fTab683->SetTab(curTabId);
        ////////////////////////////////////////////////////////////////////////

        // configure preamp gain
        if(gain > 0){
            float setVal = gain;
            for(int bid = 0; bid < t->nclients; bid++){
                if(bid > 0 && gain2 > 0){
                    setVal = gain2;
                } 
                for(int cid = 0; cid < 32; cid++)
                    fChanGain[bid][cid]->SetNumber(setVal);
            }
        }

        //***** DAQ sequence *****
        SendConfig2All();
        // clear the data container
        Reset();
        // Start taking data!
        slowerBoard = -1;
        if(RunOn == 0) StartDAQ(psNEvt);
        // save to disk
        std::string outfpn = std::string(Form("output_data/%d_%d_mppc_volt%.1lf_temp%.1lf.root", dateID, timeID, vol, temp));
        // if there is message time information, store to the subfolder
        out_fdr = std::string(Form("%d_%d_%s", dateID, msg_time, boardID.c_str()));
        if(!out_fdr.empty())
        {
            // create output folder for grouping datasets
            gROOT->ProcessLine(Form(".! mkdir -p output_data/%s", out_fdr.c_str()));
            outfpn = std::string(Form("output_data/%s/%d_%d_mppc_volt%.1lf_thr%d_gain%d_temp%.1lf.root", out_fdr.c_str(), dateID, timeID, vol, int(threshold_dac), int(gain), temperature));
        }
        tr->SaveAs(outfpn.c_str());
        SaveMetadata(outfpn, biasVoltage, temperature);

        // After data taking finishes, signal slow control I am ready.
        const char json_ready[] = " { \"daq status\" : \"ready\" } ";
        // Issue quit at request.
        const char json_quit[] = " { \"daq status\" : \"ready\" , \"quit scan\" : \"true\" } ";
        // Usually, just send DAQ ready.
        if(!QuitScan)
            SendMsg2SlowCtrl(json_ready);
        else // Otherwise, tell the control app to quit any remaining scan.
            SendMsg2SlowCtrl(json_quit);
    }


    // Grab the number of events for parameter scan.
    if(document.HasMember("drs_nevt"))
        drsNEvt = std::stoi(document["drs_nevt"].GetString());
    // Deal with dark rate scan
    if(document.HasMember("dark rate scan"))
    {
        // store FEB to scan
        if(std::string(document["dark rate scan"]["feb"].GetString()) == "All")
            for(int i = 0; i < nboard; i++) drsFebs.push_back(i);
        else drsFebs.push_back(std::stoi(document["dark rate scan"]["feb"].GetString()));
        // store channel to scan
        if(std::string(document["dark rate scan"]["ch"].GetString()) == "All")
            for(int i = 0; i < 32; i++) drsChs.push_back(i);
        else drsChs.push_back(std::stoi(document["dark rate scan"]["ch"].GetString()));
        
        // get thresholds to scan
        float thr_from = std::atof(document["dark rate scan"]["dac1_from"].GetString());
        float thr_to = std::atof(document["dark rate scan"]["dac1_to"].GetString());
        float thr_step = std::atof(document["dark rate scan"]["dac1_step"].GetString());
        // get preamp gain setting
        int preamp_gain = std::atoi(document["dark rate scan"]["preamp_gain"].GetString());
        // set up preamp gain
        for(int bid = 0; bid < t->nclients; bid++)
            for(int cid = 0; cid < 32; cid++)
                fChanGain[bid][cid]->SetNumber(preamp_gain);


        // the outermost for loop to scan through thresholds
        for(float thr = thr_from; thr <= thr_to; thr += thr_step)
        {
            if(QuitScan) break;

            // set up the threshold
            thr_vals[0] = thr;
            thr_vals[1] = thr;

            // remember the current tab
            int curTabId = fTab683->GetCurrent();
            // change values on the GUI and send configuration to FEB
            int activeFeb = BoardToMon;
            for(int bid = 0; bid < t->nclients; bid++)
            {
                BoardToMon = bid;
                fNumberEntry755->SetNumber(thr);
                fTab683->SetTab(bid);
                SelectBoard();
                SetDstMacByIndex(bid);
                GUI_UpdateThreshold();
            }

            // restore settings
            BoardToMon = activeFeb;
            fTab683->SetTab(curTabId);

            //***** Start DAQ *****
            for(unsigned int bIdx = 0; bIdx < drsFebs.size(); bIdx++)
            {
                int curFeb = drsFebs[bIdx];
                // safeguard the FEB ID
                if(curFeb >= t->nclients)
                {
                    std::cout << "FEB " << curFeb << " is not detected." << std::endl;
                    continue;
                }
                for(unsigned int cIdx = 0; cIdx < drsChs.size(); cIdx++)
                {
                    int curCh = drsChs[cIdx];
                    // Check only one channel at a time according to
                    // the current iteration in the scan.
                    for(int chItr = 0; chItr < 32; chItr++)
                    {
                        for(int fItr = 0; fItr < nboard; fItr++)
                        {
                            if((chItr == curCh) && (fItr == curFeb))
                                fChanEnaTrig[fItr][chItr]->SetState(kButtonDown);
                            else // clear all others
                                fChanEnaTrig[fItr][chItr]->SetState(kButtonUp);
                        }
                    }

                    // First, signal slow control I am busy.
                    const char json[] = " { \"daq status\" : \"busy\" } ";
                    SendMsg2SlowCtrl(json);

                    // Enable OR32
                    fChanEnaTrig[curFeb][32]->SetState(kButtonDown);
                    // apply the settings
                    SendConfig2All();
                    // clear the data container
                    Reset();
                    // Start taking data!
                    slowerBoard = curFeb;
                    if(RunOn == 0) StartDAQ(drsNEvt);
                    // save to disk
                    std::string outfpn = std::string(Form("rate_scan/raw_data/%d_%d_dark_rate_feb%d_ch%d_thr%.1lf.root", dateID, timeID, curFeb, curCh, thr));
                    if(!out_fdr.empty())
                    {
                        // create output folder for grouping datasets
                        gROOT->ProcessLine(Form(".! mkdir -p output_data/%s", out_fdr.c_str()));
                        outfpn = std::string(Form("rate_scan/raw_data/%s/%d_%d_dark_rate_feb%d_ch%d_thr%.1lf.root", out_fdr.c_str(), dateID, timeID, curFeb, curCh, thr));
                    }
                    tr->SaveAs(outfpn.c_str());
                    SaveMetadata(outfpn, biasVoltage, temperature);
                    // summarize this scan
                    RateScanSummary(std::string(outfpn), dateID, timeID, curFeb, curCh, thr, drsNEvt);

                    // After data taking finishes, signal slow control I am ready.
                    const char json_ready[] = " { \"daq status\" : \"ready\" } ";
                    SendMsg2SlowCtrl(json_ready);
                }
            }
        }
    }
}

bool ProgramFW(uint32_t startaddr=0, uint16_t blocks=1) 
{
    bool retval=1;
    buf[0]=startaddr & 0x000000ff; 
    buf[1]=(startaddr & 0x0000ff00)>>8;
    buf[2]=(startaddr & 0x00ff0000)>>16; 
    buf[3]=(blocks & 0x00FF);
    buf[4]=00; //(blocks & 0xFF00) >>8;
    t->dstmac[5] = t->macs[BoardToMon][5];
    if( t->SendCMD(t->dstmac,FEB_WR_FW,00,buf)==0) retval=0; //initiate flash programming
    for( int i=0;i<blocks;i++) {
        if(t->SendCMD(t->dstmac,FEB_DATA_FW,getCRC(fwbuf+i*1024,1024),fwbuf+i*1024)==0) retval=0;
    }
    if(retval==0) printf("Error in ProgramFW!!\n");
    return retval;

}

bool GetAndSaveFW(char *fname=NULL)
{

    bool retval=1;
    memset(fwbuf,1024*1024,00);
    for(int i=0;i<16;i++) DumpFW(i*64*1024,64);
    if(fname==NULL) return 0;
    FILE *fp=fopen(fname,"w"); 
    if(fp<=(void*) NULL) return 0;
    fwrite(fwbuf,1024,1024,fp);
    fclose(fp);
    if(retval==0) printf("Error in GetAndSaveFW!!\n");
    return retval;

}

bool UpdateFW(char *fname=NULL)
{
    bool retval=1;
    memset(fwbuf,1024*1024,00);
    printf("Opening FW file %s..\n",fname);
    FILE *fp=fopen(fname,"r");
    if(!fp) return 0;
    int count = fread(fwbuf,1024,1024,fp);
    fclose(fp);
    printf("Programming first 64 kB into FLASH addr 0x20000..\n");
    retval=ProgramFW(0x20000,64); //put FW into safe area
    if(retval==0) return 0;
    printf("Copying 64 kB FLASH from 0x20000 to 0x0..\n");
    buf[0]=0;buf[1]=0;buf[2]=0x02;buf[3]=64;buf[4]=0; //prepare for copying 64 kB from 0x20000 to 0x0
    t->SendCMD(t->dstmac,FEB_WR_FW,0x0101,buf); //perform copy
    printf("Pause 1s to let FEB perform reset..\n");
    gSystem->Sleep(1000);
    RescanNet();
    return retval;
}


bool UpdateFPGA(char *fname=NULL)
{
    bool retval=1;
    uint8_t CRC=0;
    uint8_t CRC1=0;
    uint32_t startaddr=0x80000; //put FW into second half of the FLASH
    int page64;
    memset(fwbuf,1024*1024,0xFF);
    printf("Opening FW file %s..\n",fname);
    FILE *fp=fopen(fname,"r");
    if(!fp) return 0;
    int count = fread(fwbuf,1024,1024,fp);
    fclose(fp);
    printf("Programming 512 kB into FLASH addr 0x80000..\n");
    // ProgramFW(0x80000,512); //put FW into second half of the FLASH
    for(int page64=0; page64<8; page64++)
    {
        printf("Programming 64 kB into FLASH addr 0x%08x\n",startaddr);
        gSystem->Sleep(500); 
        buf[0]=startaddr & 0x000000ff; 
        buf[1]=(startaddr & 0x0000ff00)>>8; 
        buf[2]=(startaddr & 0x00ff0000)>>16; 
        buf[3]=64;
        buf[4]=00; 
        t->dstmac[5] = t->macs[BoardToMon][5];
        t->SendCMD(t->dstmac,FEB_WR_FW,00,buf); //initiate flash programming
        for( int i=0;i<64;i++) {
            if( t->SendCMD(t->dstmac,FEB_DATA_FW,getCRC(fwbuf+(i+64*page64)*1024,1024),fwbuf+(i+64*page64)*1024) ==0) {
                retval=0;
                // printf("Error in programming 1kB block at %08x !\n",fwbuf+(i+64*page64)*1024);
            }
            gSystem->Sleep(10); 
        }
        if( retval==0)       printf("Error in programming 64kB block at %08x !\n",startaddr);
        startaddr=startaddr+64*1024;
    }
    if(retval==0) printf("Error in programmin part of UpdateFPGA!!\n");
    CRC=getCRC(fwbuf,512*1024);
    memset(fwbuf,1024*1024,00);
    printf("Verifying 512 kB block at 0x80000.. Source CRC=0x%02x\n",CRC);
    for(int page64=0; page64<8; page64++)    DumpFW(0x80000+page64*64*1024, 64);
    CRC1=getCRC(fwbuf,512*1024);   
    printf("Programmed block CRC=0x%02x..",CRC1);
    if(CRC==CRC1) printf(" OK.\n"); else {printf("ERROR !\n"); retval=0;}
    return retval;

}

void AcquireGainCalibrationData(int nevc=10000)
{
    uint32_t cmaskbefore=CHAN_MASK; //save
    int i;
    CHAN_MASK= (3 << (2*15));
    for(int sci=0; sci<16; sci++)
    {
        for(i=0; i<32;i++) //reset all chan to OFF
        {
            fChanEnaAmp[BoardToMon][i]->SetOn(kFALSE); 
            ConfigSetBit(bufSCR,1144,633+i*15,1); 
        }
        i=sci*2;
        fChanEnaAmp[BoardToMon][i]->SetOn(); 
        ConfigSetBit(bufSCR,1144,633+i*15,0);    
        i++;
        fChanEnaAmp[BoardToMon][i]->SetOn(); 
        ConfigSetBit(bufSCR,1144,633+i*15,0);    
        t->SendCMD(t->dstmac,FEB_WR_SCR,0x0000,bufSCR);
        // StartDAQ(nevc/100); ///for pedestal
        CHAN_MASK= (3 << (2*sci));
        printf("CHAN_MASK=%08x\n",CHAN_MASK);
        StartDAQ(nevc);

    }
    CHAN_MASK=cmaskbefore; //restore
}

void AcquirePedestalCalibrationData(int nevc=10000)
{
    uint32_t cmaskbefore=CHAN_MASK; //save
    int i;
    CHAN_MASK= (3 << (2*15));
    for(int sci=0; sci<16; sci++)
    {
        for(i=0; i<32;i++) //reset all chan to OFF
        {
            fChanEnaAmp[BoardToMon][i]->SetOn(kFALSE); 
            ConfigSetBit(bufSCR,1144,633+i*15,1); 
        }
        i=sci*2;
        fChanEnaAmp[BoardToMon][i]->SetOn(); 
        ConfigSetBit(bufSCR,1144,633+i*15,0);    
        i++;
        fChanEnaAmp[BoardToMon][i]->SetOn(); 
        ConfigSetBit(bufSCR,1144,633+i*15,0);    
        t->SendCMD(t->dstmac,FEB_WR_SCR,0x0000,bufSCR);
        StartDAQ(nevc); ///for pedestal
        CHAN_MASK= (3 << (2*sci));
        // printf("CHAN_MASK=%08x\n",CHAN_MASK);
        // StartDAQ(nevc);

    }
    CHAN_MASK=cmaskbefore; //restore
}

void Calibrate(int nevcc=10000)
{
    char strnm[32];
    tr->Reset();
    AcquirePedestalCalibrationData(nevcc/5);
    sprintf(strnm,"Pedestal_SN%03d.root",t->macs[BoardToMon][5]);
    tr->SaveAs(strnm);
    tr->Reset();
    AcquireGainCalibrationData(nevcc);
    sprintf(strnm,"Gain_SN%03d.root",t->macs[BoardToMon][5]);
    tr->SaveAs(strnm);
}

void MakeProfileTest()
{
    printf("Rescanning the net..\n");
    RescanNet();
    Reset();
    //printf("Set SiPM bias to 0V..\n");
    //HVOF();
    //printf("Take profile for pedestals..\n");
    printf("Set SiPM bias ON..\n");
    HVON();
    printf("Starting DAQ for %d seconds..\n",int(fNumberEntryTME->GetNumber()));
    if(RunOn==0) StartDAQ();
    printf("Set SiPM bias to 0V..\n");
    HVOF();
    printf("Done.\n");
}

void ConfigSetFIL(uint32_t mask1)
{
    uint8_t bufFIL[256]; 
    *((uint32_t*)(&(bufFIL[0])))=mask1;
    // *((uint32_t*)(&(bufFIL[4])))=mask2;
    // *((uint32_t*)(&(bufFIL[8])))=mask3;
    // *((uint8_t*)(&(bufFIL[12])))=majority;

    for(int feb=0; feb<t->nclients; feb++)
    {
        SetDstMacByIndex(feb);
        t->SendCMD(t->dstmac,FEB_WR_FIL,0x0000,bufFIL); 
    }
}
