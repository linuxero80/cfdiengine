package com.maxima.bbgum;

import java.util.HashMap;
import java.util.Map;

public class MaximaFactory<I,T> {
    Map<I, Class<? extends T>> s;
    public MaximaFactory(){
        this.s = new HashMap<I, Class<? extends T>>();
    }

    public boolean isSupported(final I id) {
        return (this.s.get(id) != null)? true : false;
    }

    public T getEntity(I id) throws InstantiationException, IllegalAccessException {
        return s.get(id).newInstance();
    }
    
    public void subscribe(I id, Class<? extends T> x) {
        this.s.put(id, x);
    }
}
