SELECT zdb.define_tokenizer('words', '{
    "type": "simple_pattern",
    "pattern": "\\w+"
}');
SELECT zdb.define_filter('nltk_stopwords', '{
    "type": "stop",
    "ignore_case": true,
    "stopwords_path": "./english_stopwords.txt"
}');
SELECT zdb.define_analyzer('preprocess_lemmatise', '{
    "type": "custom",
    "tokenizer": "words",
    "filter": [
        "lowercase",
        "nltk_stopwords",
        "kstem"
    ]
}');
CREATE DOMAIN preprocess_lemmatise as text;

CREATE TABLE IF NOT EXISTS debate (
    debate_id varchar(255),
    title varchar(255),
    debate_date timestamp NOT NULL,
    PRIMARY KEY(debate_id)
);
CREATE TABLE IF NOT EXISTS scraped_url (
    url varchar(255),
    last_scraped timestamp not null,
    PRIMARY KEY (url)
);
CREATE TABLE IF NOT EXISTS petition (
    petition_id int,
    state varchar(255),
    title preprocess_lemmatise,
    content preprocess_lemmatise,
    processed_content VARCHAR(255) [],
    created_at timestamp not null,
    closed_at timestamp,
    updated_at timestamp,
    response_threshold timestamp,
    debate_threshold timestamp,
    moderation_threshold timestamp,
    rejected_at timestamp,
    rejected_reason varchar(255),
    signatures int not null,
    response_summary preprocess_lemmatise,
    response_details preprocess_lemmatise,
    debate_id varchar(255),
    topics varchar(255) [],
    PRIMARY KEY(petition_id),
    CONSTRAINT debate_fk FOREIGN KEY(debate_id) REFERENCES debate(debate_id) ON DELETE
    SET NULL ON UPDATE CASCADE
);
CREATE INDEX petitionidx ON petition USING zombodb ((petition.*)) WITH (url = 'http://localhost:9200/');
CREATE TABLE IF NOT EXISTS constituency (
    ons_code VARCHAR(255),
    name VARCHAR(255),
    PRIMARY KEY(ons_code)
);
CREATE TABLE IF NOT EXISTS mp (
    mp_id serial,
    ons_code varchar(255) not null,
    name varchar(255) not null,
    party varchar(255) not null,
    term_start timestamp not null,
    term_end timestamp,
    PRIMARY KEY(mp_id),
    CONSTRAINT constituency_fk FOREIGN KEY(ons_code) REFERENCES constituency(ons_code) ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS signature_by_constituency (
    petition_id int,
    ons_code VARCHAR(255) NOT NULL,
    count int,
    PRIMARY KEY(petition_id, ons_code),
    CONSTRAINT petition_fk FOREIGN KEY(petition_id) REFERENCES petition(petition_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT mp_fk FOREIGN KEY(ons_code) REFERENCES constituency(ons_code) ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS signature_by_country (
    petition_id int,
    country VARCHAR(255) NOT NULL,
    count int,
    CONSTRAINT petition_fk FOREIGN KEY(petition_id) REFERENCES petition(petition_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY(petition_id, country)
);
CREATE TABLE IF NOT EXISTS vignette (
    date timestamp,
    debate_id varchar(255),
    p_id int,
    content preprocess_lemmatise,
    PRIMARY KEY(mp_id, debate_id)
);
CREATE INDEX vignetteidx ON vignette USING zombodb ((vignette.*)) WITH (url = 'http://localhost:9200/');
CREATE INDEX vignette_date_idx ON vignette(date);
CREATE TABLE IF NOT EXISTS tweet (
    tweet_id serial,
    petition_id int,
    user_id bigint,
    verified boolean,
    user_followers int,
    user_friends int,
    created_at timestamp,
    likes int,
    retweets int,
    replies int,
    PRIMARY KEY(tweet_id),
    CONSTRAINT tweet_fk FOREIGN KEY(petition_id) REFERENCES petition(petition_id) ON DELETE
    SET NULL ON UPDATE CASCADE
);