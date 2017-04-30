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
    public void handlerOutComming(EventBlackBox v, Action action) {

    }

    @Override
    public void handlerInComming(EventBlackBox v, Action action) {

    }

    @Override
    public void handlerTimeOut(EventBlackBox v, Action action) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public int handlerGetConclusion(EventBlackBox v) {
        return this.conclusion;
    }

    public abstract int analyzeAck(Action action);
}
