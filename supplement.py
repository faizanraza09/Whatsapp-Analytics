from prometheus_client import Counter, Summary, Gauge, Histogram

class REGISTRY:
    inited = False
    @classmethod
    def get_metrics(cls):
        if cls.inited:
            cls.c.inc()
            return cls
        else:
            # Register your metrics here
            cls.c = Counter('number_of_requests', 'Cumulative http requests till date')
            cls.REQUEST_TIME=Gauge('wordcloud_loading_time', 'Time spent in processing request')
            cls.wcr=Counter('number_of_wordclouds','Total number of wordclouds created till date')
            cls.udf=Counter('number_of_user_dataframes','Total number of user dataframes created till date')
            cls.dowbp=Counter('number_of_day_of_week_barplots','Total number of Messages per Day of week barplots created till date')
            cls.lppdf=Counter('number_of_len_per_person_dataframes','Total number of length per person dataframes created till date')
            cls.esdf=Counter('number_of_emoji_stats_dataframes','Total number of emoji stats dataframes created till date ')
            cls.inited = True
            return cls