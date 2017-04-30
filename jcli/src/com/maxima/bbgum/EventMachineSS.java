package com.maxima.bbgum;

public abstract class EventMachineSS implements EventController {

    private boolean endFlowFlag;
    private int conclusion;

    public EventMachineSS(){
        this.endFlowFlag = false;
        this.conclusion = 0;
    }

    @Override
    public boolean handlerIsFlowTerm(EventBlackBox v) {
        return this.endFlowFlag;
    }

    @Override
    public void handlerOutComming(EventBlackBox v, DatAction action) {

    }

    @Override
    public void handlerInComming(EventBlackBox v, DatAction action) {

    }

    @Override
    public void handlerTimeOut(EventBlackBox v, DatAction action) {

    }

    @Override
    public int handlerGetConclusion(EventBlackBox v) {
        return this.conclusion;
    }

    public abstract int analyzeAck(DatAction action);
}
