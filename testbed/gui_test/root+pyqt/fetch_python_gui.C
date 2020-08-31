#include <iostream>
#include "rapidjson/document.h"
#include <unistd.h>
#include <zmq.hpp>

#include <TGButton.h>
#include <TGFrame.h>
#include <TGLabel.h>
#include <TGTextEdit.h>
#include <TGTextEntry.h>
#include <TPython.h>
#include <TROOT.h>
#include <TSystem.h>
// #include <TThread.h>
#include <TVirtualX.h>
#include <RQ_OBJECT.h>

using namespace rapidjson;

class MyDialog
{

    RQ_OBJECT("MyDialog")

private:
    TGTransientFrame *fMain;
    TGCompositeFrame *fHor1;
    TGButton *fOk;
    TGGroupFrame *fGframe;
    TGTextEntry *fText;
    TGLabel *fLabel;

public:
    MyDialog(const TGWindow *p, const TGWindow *main, UInt_t w, UInt_t h,
             UInt_t options = kVerticalFrame);
    virtual ~MyDialog();

    // slots
    void CloseWindow();
    void DoOK();
    void DoSetlabel();
};

MyDialog::MyDialog(const TGWindow *p, const TGWindow *main, UInt_t w, UInt_t h,
                   UInt_t options)
{
    // 1st: to create an window with respect to its parent (main) window

    fMain = new TGTransientFrame(p, main, w, h, options);
    fMain->Connect("CloseWindow()", "MyDialog", this, "CloseWindow()");

    fHor1 = new TGHorizontalFrame(fMain, 80, 20, kFixedWidth);
    fOk = new TGTextButton(fHor1, " &Ok ", 1);
    fOk->Connect("Clicked()", "MyDialog", this, "DoOK()");
    fHor1->AddFrame(fOk, new TGLayoutHints(kLHintsTop | kLHintsLeft | kLHintsExpandX,
                                           4, 4, 4, 4));
    fHor1->Resize(150, fOk->GetDefaultHeight());
    fMain->AddFrame(fHor1, new TGLayoutHints(kLHintsBottom | kLHintsRight, 2, 2, 5, 1));

    // 2nd: create widgets in the dialog
    fText = new TGTextEntry(fMain, new TGTextBuffer(100));
    fText->SetToolTipText("Enter the label and hit Enter key");
    fText->Connect("ReturnPressed()", "MyDialog", this, "DoSetlabel()");
    fMain->AddFrame(fText, new TGLayoutHints(kLHintsTop | kLHintsLeft, 5, 5, 5, 5));
    fGframe = new TGGroupFrame(fMain, "Last Input");
    fLabel = new TGLabel(fGframe, "No Intut ");
    fGframe->AddFrame(fLabel, new TGLayoutHints(kLHintsTop | kLHintsLeft, 5, 5, 5, 5));
    fMain->AddFrame(fGframe, new TGLayoutHints(kLHintsExpandX, 2, 2, 1, 1));
    fText->Resize(150, fText->GetDefaultHeight());

    fMain->MapSubwindows();
    fMain->Resize(fMain->GetDefaultSize());

    // position of the dialog relative to the parent's window
    Window_t wdum;
    int ax, ay;
    gVirtualX->TranslateCoordinates(main->GetId(), fMain->GetParent()->GetId(),
                                    (Int_t)(((TGFrame *)main)->GetWidth() - fMain->GetWidth()) >> 1,
                                    (Int_t)(((TGFrame *)main)->GetHeight() - fMain->GetHeight()) >> 1,
                                    ax, ay, wdum);
    fMain->Move(ax, ay);

    fMain->SetWindowName("My Dialog");

    fMain->MapWindow();
}

MyDialog::~MyDialog()
{
    delete fText;
    delete fLabel;
    delete fOk;
    delete fHor1;
    delete fGframe;

    delete fMain;
}

void MyDialog::CloseWindow()
{
    // Called when the window is closed via the window manager.

    delete this;
}

void MyDialog::DoSetlabel()
{
    printf("\nThe Enter key is pressed\n");

    fLabel->SetText(fText->GetBuffer()->GetString());
    fGframe->Layout();
}

void MyDialog::DoOK()
{
    TQObject::Disconnect(fText, "ReturnPressed()", this, "DoSetlabel()");
    printf("\nThe OK button is pressed\n");
    fMain->SendCloseMessage();
}

class MyMainFrame
{
    RQ_OBJECT("MyMainFrame")
private:
    TGMainFrame *fMain;
    TGTextEntry *edt_msg;
    TGTextEdit*  fMsgDisplay;
    // TThread*     fMsgThread;
    TTimer*      fTimerPoll;

    // zmq variables
    zmq::context_t fContext;
    zmq::socket_t fSocket;
    // zmq::pollitem_t fItem;
    std::vector<zmq::pollitem_t> fP;

public:
    MyMainFrame(const TGWindow *p, UInt_t w, UInt_t h);
    virtual ~MyMainFrame();
    void FetchPyqtApp();
    void SendMessage();
    // static void* receiveFunction(void *arg);
    void PollMessage();
    void ProcessMessage(std::string);
};

MyMainFrame::MyMainFrame(const TGWindow *p, UInt_t w, UInt_t h)
    // : fContext(1), fSocket(fContext, zmq::socket_type::pair), fMsgThread(0)
    : fContext(1), fSocket(fContext, zmq::socket_type::pair)
{
    // zmq business
    try {
        fSocket.bind("tcp://*:5556");
        // fItem = { static_cast<void*>(fSocket), 0, ZMQ_POLLIN, 0 };
        fP.push_back({ static_cast<void*>(fSocket), 0, ZMQ_POLLIN, 0 });
    }
    catch (...){
        std::cout << "Socket related errors..." << std::endl;
    }
    // usleep(1000000);

    // zmq receiver setup
    // fMsgThread = new TThread("MsgThread", (void(*)(void*))&receiveFunction, (void*)this);
    // fMsgThread->Run();
    // Instead of using thread, try timer instead.
    fTimerPoll = new TTimer();
    fTimerPoll->Connect("Timeout()", "MyMainFrame", this, "PollMessage()");
    fTimerPoll->Start(100, kFALSE);

    // Create a main frame
    fMain = new TGMainFrame(p, w, h);

    // Create a horizontal frame widget with buttons
    TGHorizontalFrame *hframe = new TGHorizontalFrame(fMain, 200, 40);
    edt_msg = new TGTextEntry(hframe);
    hframe->AddFrame(edt_msg, new TGLayoutHints(kLHintsCenterX, 5, 5, 3, 4));

    // add a send message button
    TGTextButton *btn_send = new TGTextButton(hframe, "Send");
    btn_send->Connect("Clicked()", "MyMainFrame", this, "SendMessage()");
    hframe->AddFrame(btn_send, new TGLayoutHints(kLHintsCenterX,
                                                 5, 5, 3, 4));

    TGTextButton *fetch = new TGTextButton(hframe, "&Fetch");
    fetch->Connect("Clicked()", "MyMainFrame", this, "FetchPyqtApp()");
    hframe->AddFrame(fetch, new TGLayoutHints(kLHintsCenterX,
                                              5, 5, 3, 4));

    TGTextButton *exit = new TGTextButton(hframe, "&Exit",
                                          "gApplication->Terminate(0)");
    hframe->AddFrame(exit, new TGLayoutHints(kLHintsCenterX,
                                             5, 5, 3, 4));
    fMain->AddFrame(hframe, new TGLayoutHints(kLHintsCenterX,
                                              2, 2, 2, 2));

    // Create another horizontal frame widget with a text edit
    TGVerticalFrame *vframe = new TGVerticalFrame(fMain, 200, 160);
    fMsgDisplay = new TGTextEdit(vframe, 260, 120, kSunkenFrame | kDoubleBorder);
    vframe->AddFrame(fMsgDisplay, new TGLayoutHints(kLHintsCenterX,
                                                    5, 5, 3, 4));
    fMain->AddFrame(vframe, new TGLayoutHints(kLHintsCenterX,
                                              2, 2, 2, 2));

    // Set a name to the main frame
    fMain->SetWindowName("Simple Example");

    // Map all subwindows of main frame
    fMain->MapSubwindows();

    // Initialize the layout algorithm
    fMain->Resize(fMain->GetDefaultSize());

    // Map main frame
    fMain->MapWindow();
}

MyMainFrame::~MyMainFrame()
{
    // flush the socket
    fSocket.close();
    // Clean up used widgets: frames, buttons, layout hints
    fMain->Cleanup();
    delete fMain;
}

void MyMainFrame::FetchPyqtApp()
{
    // Source:
    // https://root-forum.cern.ch/t/dialogue-box/1511/5
    // Testing a dialog box
    // new MyDialog(gClient->GetRoot(), fMain, 400, 200);
    // Printf("Create MyDialog window...");

    // TPython::ExecScript("main_control.py");
    // gSystem->Exec("printenv | ack -i conda"); // check environment
    // gROOT->ProcessLine(".! python main_control.py &");

    // same as TROOT::ProcessLine but more elegant
    gSystem->Exec("python main_control.py &");

    // below is code to get terminal output
    TString s = gSystem->GetFromPipe("printenv | ack -i conda");
    // std::cout << s.Data() << std::endl;
}

void MyMainFrame::PollMessage()
{
    // std::cout << "hi" << std::endl;
    zmq::message_t message;
    // zmq::pollitem_t items [] = {
    //     { static_cast<void*>(fSocket), 0, ZMQ_POLLIN, 0 }
    // };
    // zmq::poll (fItem, 2, 0);
    // std::vector<zmq::pollitem_t> p = {{fSocket, 0, ZMQ_POLLIN, 0}};
    // zmq::poll (&items [0], 2, 0);
    zmq::poll(fP.data(), 1, 0); // changed from zmq::poll(fP.data(), 2, 1); So far now segfault...
    
    if (fP[0].revents & ZMQ_POLLIN) {
        zmq::recv_result_t rec_res = fSocket.recv(message, zmq::recv_flags::dontwait);
        //  Process task
        std::string rpl = std::string(static_cast<char*>(message.data()), message.size());
        // std::cout << rpl << std::endl;
        // fMsgDisplay->InsLine(fMsgDisplay->RowCount(), rpl.c_str());
        fMsgDisplay->AddLine(rpl.c_str());
        fMsgDisplay->Update();
        ProcessMessage(rpl);
    }
}

void MyMainFrame::ProcessMessage(std::string msg)
{
    Document document;
    document.Parse(msg.c_str());

    for (Value::ConstMemberIterator itr = document["vol"].MemberBegin(); itr != document["vol"].MemberEnd(); ++itr)
        std::cout << itr->name.GetString() << std::endl;
}

// void* MyMainFrame::receiveFunction(void* arg)
// {
//     MyMainFrame *main = (MyMainFrame *)arg;
//     // main->fSocket.bind("tcp://*:5556");
//     std::cout << "hi" << std::endl;

//     // start the receiver loop
//     while (true)
//     {
//         zmq::message_t request;
//         // main->fSocket.recv(&request);
//         // std::string rpl = std::string(static_cast<char*>(request.data()), request.size());
//         // main->fMsgDisplay->Clear();
//         // TGText txt;
//         // txt.LoadBuffer(rpl.c_str());
//         // main->fMsgDisplay->AddText(&txt);
//     }

//     return 0;
// }

void MyMainFrame::SendMessage()
{
    std::string msg(edt_msg->GetText());
    //  Send reply back to client
    zmq::message_t reply(msg.length());
    memcpy(reply.data(), msg.c_str(), msg.length());
    fSocket.send(reply, zmq::send_flags::none);
}

void fetch_python_gui()
{
    new MyMainFrame(gClient->GetRoot(), 200, 200);
}
