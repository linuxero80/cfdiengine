package com.maxima.bbgum;

public class FeedBackData {

    private int result;
    private byte[] data;

    public FeedBackData() {
        this.result = 0;
    }
    public int getResult() {
        return result;
    }

    public void setResult(int result) {
        this.result = result;
    }

    public byte[] getData() {
        return data;
    }

    public void setData(byte[] data) {
        this.data = data;
    }   
}
