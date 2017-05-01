package com.maxima.bbgum;

interface EventController {
    boolean handlerIsFlowTerm(EventBlackBox v);
    void handlerOutComming(EventBlackBox v, Action action) throws SessionError;
    void handlerInComming(EventBlackBox v, Action action) throws SessionError;
    void handlerTimeOut(EventBlackBox v, Action action);
    int handlerGetConclusion(EventBlackBox v);
    byte[] handlerGetData(EventBlackBox v);
}
