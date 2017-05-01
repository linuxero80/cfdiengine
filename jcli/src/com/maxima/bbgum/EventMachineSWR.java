package com.maxima.bbgum;

public abstract class EventMachineSWR implements EventController {

    private enum Progress {
        SEND,
        RECIVE_ACK,
        RECIVE_RESPONSE,
        SEND_ACK
    }

    boolean endFlowFlag;
    private int conclusion;
    public byte[] bufferWithResponse;

    Progress p;

    public EventMachineSWR() {
        this.p = Progress.SEND;
        this.endFlowFlag = false;
    }

    @Override
    public boolean handlerIsFlowTerm(EventBlackBox v) {
        return this.endFlowFlag;
    }

    @SuppressWarnings("incomplete-switch")
    @Override
    public void handlerInComming(EventBlackBox v, Action action) throws SessionError {
        switch (this.p) {
            case RECIVE_ACK: {
                int response = analyzeAck(action);

                if (response == 0) {
                    this.p = Progress.RECIVE_RESPONSE;
                } else {
                    this.conclusion = response;
                    this.endFlowFlag = true;
                }
                break;
            }
            case RECIVE_RESPONSE: {
                byte[] dataForAck = new byte[Frame.ACTION_ACK_DATA_SIZE];
                int result = analyzeData(action);

                if (result == 0) {
                    dataForAck[0] = Frame.DAT_ACK;
                } else {
                    this.conclusion = result;
                    dataForAck[0] = Frame.DAT_NAK;
                }

                dataForAck[1] = (byte)result;
                Monitor mc = v.getMonitor();
                Action a = new Action();
                a.setArchetype(Frame.calcIdForACKorNAK(action.getArchetype()));
                a.setTransNum(action.getTransNum());
                a.setBuffer(dataForAck);
                mc.send(a);
                this.endFlowFlag = true;
                break;
            }
        }
    }

    @Override
    public void handlerOutComming(EventBlackBox v, Action action) throws SessionError {
        this.p = Progress.RECIVE_ACK;
        Monitor mc = v.getMonitor();
        mc.send(action);
    }

    @Override
    public void handlerTimeOut(EventBlackBox v, Action action) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public ServerReply handlerGetReply(EventBlackBox v) {
        ServerReply reply = new ServerReply();
        reply.setReplyCode(this.conclusion);
        if (this.conclusion == 0) reply.setReplyBuffer(this.bufferWithResponse);
        return reply;
    }

    public abstract int analyzeAck(Action action);

    public abstract int analyzeData(Action action);
}
