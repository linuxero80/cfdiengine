package com.maxima.bbgum;

public class DatAction {

    private byte id;
    private byte transaction;
    private byte[] data;

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
