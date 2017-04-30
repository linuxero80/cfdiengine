package com.maxima.bbgum;

public interface EventController {
    
    boolean handlerIsFlowTerm(EventBlackBox v);
    void handlerOutComming(EventBlackBox v, DatAction action);
    void handlerInComming(EventBlackBox v, DatAction action);
    void handlerTimeOut(EventBlackBox v, DatAction action);
    int handlerGetConclusion(EventBlackBox v);
}
