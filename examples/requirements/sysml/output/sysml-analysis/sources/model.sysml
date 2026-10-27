package CanSat {
    part def CS1 {
        part structure : Structure;
        part power : Power;
        part fcu : FlightComputer;
        part sensors : Sensors;
        part comms : Comms;
    }
    part def Structure;
    part def Power;
    part def FlightComputer;
    part def Sensors;
    part def Comms;
    part def GroundStation;

    requirement def SampleRate;
    requirement def SupplyDuration;
    requirement def SamplingPeriod;
    requirement sampleRate : SampleRate;
    requirement supplyDuration : SupplyDuration;
    requirement samplingPeriod : SamplingPeriod;

    action def SelfTest;
    action def SamplePack;
    action def Transmit;
    action def EnterSafe;
    action def Heartbeat;
    action def StoreData;

    state def Mission {
        state standby;
        state armed;
        state ascent;
        state descent;
        state landed;
        state replay;
        state safe;
        transition armed_to_ascent first armed then ascent;
        transition ascent_to_descent first ascent then descent;
        transition descent_to_landed first descent then landed;
        transition landed_to_replay first landed then replay;
    }
}
