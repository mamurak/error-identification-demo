package com.redhat;

import org.apache.camel.Exchange;
import org.apache.camel.Processor;
import io.opentelemetry.api.trace.Span;
import io.quarkus.arc.Unremovable;
// import io.opentelemetry.api.common.Attributes;
// import io.opentelemetry.api.common.AttributeKey;
// import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

@Named("messageProcessor")
@Singleton
@Unremovable
//@ApplicationScoped

public class MessageProcessor implements Processor {
    @Override
    public void process(Exchange exchange) {
        System.out.println("inside MessageProcessor");
        String body=exchange.getIn().getBody(String.class);        
        System.out.println("inside MessageProcessor currernt span"+ Span.current());
        Span.current().addEvent("EndPoint uri="+exchange.getFromEndpoint().getEndpointUri()+" Message Body="+body);
    }
}
