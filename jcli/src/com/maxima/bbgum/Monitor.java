package com.maxima.bbgum;

final class Monitor {

    static final int TRANSACTION_NUM_START_VALUE = 1;
    static final int TRANSACTION_NUM_LAST_VALUE = 253;
    static final int TRANSACTION_NUM_INCREMENT =  2;
    static final int MAX_NODES = 255;

    private int nextNum;
    private Session session;
    private Transaction[] pool;
    private Object poolMutex;
    private EventBlackBox blackBox;

    public Monitor(Session session) {
        this.session = session;
        {
            // Initialization of elements for transactions pool
            this.nextNum = Monitor.TRANSACTION_NUM_START_VALUE;
            this.poolMutex = new Object();
            this.pool = new Transaction[Monitor.MAX_NODES];

            int iter = 0;
            for (; iter < Monitor.MAX_NODES; iter++) this.pool[iter] = null;
        }
        this.blackBox = new EventBlackBox(this);
    }

    private int requestNextNum() throws SessionError {

        // The current function must only be called
        // by pushBuffer function.

        int index = this.nextNum;

        if ((this.pool[index] != null) &&
            (index == Monitor.TRANSACTION_NUM_LAST_VALUE )) {

            // From the first shelf we shall start
            // the quest of an available one if
            // next one was ocuppied and the last one.

            index = Monitor.TRANSACTION_NUM_START_VALUE;
        }

        if (this.pool[index] == null) {

            // When the shelf is available we shall return it
            // before we shall set nextNum variable up for
            // later calls to current function.

            if (index == Monitor.TRANSACTION_NUM_LAST_VALUE) {
                this.nextNum = Monitor.TRANSACTION_NUM_START_VALUE;
            } else {
                this.nextNum = index + Monitor.TRANSACTION_NUM_INCREMENT;
            }
            return index;
        }

        {
            // If you've reached this code block my brother, so...
            // you migth be in trouble soon. By the way you seem
            // a lucky folk and perhaps you would find a free
            // shelf by performing sequential search with awful
            // linear time. Otherwise the matter is fucked :(

            int i = 0;

            do {
                index += Monitor.TRANSACTION_NUM_INCREMENT;
                i++;
            } while ((this.pool[index] != null) && (i < Monitor.MAX_NODES));

            if (i == (Monitor.MAX_NODES - 1)) {
                String msg = "Poll of transactions to its maximum capacity";
                throw new SessionError(msg);
            }
            this.nextNum = index + Monitor.TRANSACTION_NUM_INCREMENT;
            return index;
        }
    }

    private boolean isServerTransaction(final int num) {
        return ((num % 2) == 0);
    }

    private synchronized Transaction getTransactionFromPoll(int index) {
        return (this.pool[index] != null) ? this.pool[index] : null;
    }

    private synchronized void destroyTransactionInPoll(int index) {
        this.pool[index] = null;
    }

    public void recive(Action action) {
        // Receives an action from upper layer

    }

    public void send(Action action) {
        // Sends action to upper layer
        this.session.deliver(action);
    }

    public FeedBackData pushBuffer(final byte archetype, final byte[] buffer, final boolean block) throws SessionError {
        FeedBackData fb = new FeedBackData();

        Action a = new Action();
        a.setArchetype(archetype);
        a.setBuffer(buffer);
        Transaction t = new Transaction(archetype, block, false);
        try {

            synchronized (poolMutex) {
                a.setTransNum((byte) this.requestNextNum());
                this.pool[a.getTransNum() & 0xff] = t;
            }

            this.blackBox.outComming(t.getController(), a);

            if (t.isBlockingMode()) {
                t.sleep();
                fb.setResult(this.blackBox.getConclusion(t.getController()));
                if (fb.getResult() == 0) fb.setData(this.blackBox.getData(t.getController()));

                //Destroy node
                synchronized (poolMutex) {
                    this.pool[a.getTransNum() & 0xff] = null;
                }

            }

        } catch (Exception ex) {
            throw new SessionError("!!!");
        }

        return fb;
    }
}
