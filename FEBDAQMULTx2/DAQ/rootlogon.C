#include "TROOT.h"
#include "TSystem.h"
void rootlogon()
{
    gSystem->Load("libFEBDTP.so");
    gSystem->AddIncludePath("-I$CONDA_PREFIX/include");
    gSystem->AddLinkedLibs("$CONDA_PREFIX/lib/libzmq.so");
}
