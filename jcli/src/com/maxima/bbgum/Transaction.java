package com.maxima.bbgum;


public class Transaction {

    private byte actionId;
    private boolean blockingMode;
    private boolean modeServer;
    private EventController c;
    private Object wakeUpMutex = new Object();

    public Transaction(byte actionId, boolean block, boolean mode) {
        this.actionId = actionId;
        this.blockingMode = block;
        this.modeServer = mode;


    }
    
    public void sleep() throws InterruptedException{
        synchronized (wakeUpMutex) {
            wakeUpMutex.wait();
        }
    }

    public void wakeUp(){
        synchronized (wakeUpMutex) {
            wakeUpMutex.notify();
        }        
    }

    public EventController getController() {
        return c;
    }

    public byte getActionId() {
        return actionId;
    }

    public boolean isModeServer() {
        return modeServer;
    }

    public boolean isBlockingMode() {
        return blockingMode;
    }
}
