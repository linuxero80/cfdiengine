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
    public void handlerOutComming(EventBlackBox v, Action action) throws SessionError {
        Monitor mc = v.getMonitor();
        mc.send(action);
    }

    @Override
    public void handlerInComming(EventBlackBox v, Action action) throws SessionError {
        this.conclusion = analyzeAck(action);
        this.endFlowFlag = true;
    }

    @Override
    public void handlerTimeOut(EventBlackBox v, Action action) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public ServerReply handlerGetReply(EventBlackBox v) {
        ServerReply reply = new ServerReply();
        reply.setReplyCode(this.conclusion);
        {
            byte[] a = {0};
            reply.setReplyBuffer(a);
        }
        return reply;
    }

    public abstract int analyzeAck(Action action);
}
