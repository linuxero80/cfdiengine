package com.maxima.bbgum;

public abstract class EventMachineSWR implements EventController {

    private enum Progress {
        SEND,
        RECIVE_ACK,
        RECIVE_RESPONSE,
        SEND_ACK_OR_NAK
    }

    boolean endFlowFlag;
    private int conclusion;
    public byte[] bufferWithResponse;

    Progress p;

    public SendWithResponse() {
        this.p = Progress.SEND;
        this.endFlowFlag = false;
    }

    @Override
    public boolean handlerIsFlowTerm(EventBlackBox v) {
        return this.endFlowFlag;
    }

    @SuppressWarnings("incomplete-switch")
    @Override
    public void handlerInComming(EventBlackBox v, DatAction action) {
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
                byte[] dataForAck = new byte[DatFrame.DAT_ACTION_ACK_DATA_SIZE];
                int result = analyzeData(action);

                if (result == 0) {
                    dataForAck[0] = DatFrame.DAT_ACK;
                } else {
                    this.lifeResume = result;
                    dataForAck[0] = DatFrame.DAT_NAK;
                }

                dataForAck[1] = (byte)result;
                Monitor mc = v.getMonitor();
                DatAction newSduActionToAssemble = new DatAction();
                newSduActionToAssemble.setId(DatFrame.calcActionIdForACKorNAK(action.getId()));
                newSduActionToAssemble.setTransaction(action.getTransaction());
                newSduActionToAssemble.setData(dataForAck);
                mc.sendActionToDeliver(newSduActionToAssemble);
                this.endFlowFlag = true;
                break;
            }
        }
    }

    @Override
    public void handlerOutComming(EventBlackBox v, DatAction action) {
        this.p = Progress.RECIVE_ACK;
        Monitor mc = v.getMonitor();
        mc.sendToDeliver(action);
    }

    @Override
    public void handlerTimeOut(EventBlackBox v, DatAction action) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public int handlerGetConclusion(EventBlackBox v) {
        return this.conclusion;
    }

    public abstract int analyzeAck(DatAction action);

    public abstract int analyzeData(DatAction action);
}
