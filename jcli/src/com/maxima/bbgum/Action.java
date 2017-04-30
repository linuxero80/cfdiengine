package com.maxima.bbgum;

public class Action {

    private byte id;
    private byte transaction;
    private byte[] data;

    public Action() {

    }

    public Action(final byte[] data) {

        if (data.length > Frame.FRAME_BODY_MAX_LENGTH) {
            // we should throw an exception here
            System.out.println(" DatAction can not be bigger than " + Frame.FRAME_BODY_MAX_LENGTH + " " + "bytes");
        }

        this.setId(data[0]);
        this.setTransaction(data[1]);

        byte dataForAction[] = new byte[data.length - Frame.ACTION_FLOW_INFO_SEGMENT_LENGTH];
        System.arraycopy(data,
            Frame.ACTION_FLOW_INFO_SEGMENT_LENGTH,
            dataForAction, 0, dataForAction.length);
        this.setData(dataForAction);
    }

    public byte getId() {
        return id;
    }

    public void setId(byte id) {
        this.id = id;
    }

    public byte getTransaction() {
        return transaction;
    }

    public void setTransaction(byte transaction) {
        this.transaction = transaction;
    }

    public byte[] getData() {
        return data;
    }

    public void setData(byte[] data) {
        this.data = data;
    }
}
