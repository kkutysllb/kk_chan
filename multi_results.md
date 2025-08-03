{
    "meta": {
        "symbol": "300750.SZ",
        "levels": [
            "daily",
            "30min",
            "5min"
        ],
        "analysis_time": "2025-08-03T21:46:55.900319",
        "days": 90
    },
    "results": {
        "daily": {
            "meta": {
                "level": "daily",
                "analysis_level": "standard",
                "data_count": 66
            },
            "structures": {
                "fenxing_count": 13,
                "bi_count": 12,
                "seg_count": 2,
                "zhongshu_count": 0
            },
            "dynamics": {
                "backchi_count": 0,
                "buy_sell_points_count": 0,
                "buy_points_count": 0,
                "sell_points_count": 0,
                "buy_sell_points": [],
                "backchi": []
            },
            "evaluation": {
                "trend_direction": null,
                "trend_strength": 0.0,
                "risk_level": 0.0,
                "confidence_score": 0.0,
                "recommended_action": null,
                "level_consistency_score": 0.0
            },
            "latest_signals": []
        },
        "30min": {
            "meta": {
                "level": "30min",
                "analysis_level": "standard",
                "data_count": 436
            },
            "structures": {
                "fenxing_count": 91,
                "bi_count": 90,
                "seg_count": 13,
                "zhongshu_count": 3
            },
            "dynamics": {
                "backchi_count": 1,
                "buy_sell_points_count": 1,
                "buy_points_count": 1,
                "sell_points_count": 0,
                "buy_sell_points": [
                    {
                        "id": "signal_0",
                        "name": "3buy",
                        "coord": [
                            "2025-06-09 10:30",
                            250.88
                        ],
                        "value": 250.88,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.20854133509635092,
                        "reliability": 1.0,
                        "confirmed_higher": false,
                        "confirmed_lower": true,
                        "kline_index": 210,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-16 09:30",
                            "end_time": "2025-05-12 11:30",
                            "low": 231.2,
                            "high": 238.66,
                            "strength": 0.5141295340306796
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-28 10:30",
                            "end_time": "2025-06-09 10:30",
                            "strength": 0.20854133509635092
                        }
                    }
                ],
                "backchi": []
            },
            "evaluation": {
                "trend_direction": null,
                "trend_strength": 0.0,
                "risk_level": 0.0,
                "confidence_score": 0.0,
                "recommended_action": null,
                "level_consistency_score": 1.0
            },
            "latest_signals": [
                {
                    "type": "三类买点",
                    "price": 250.88,
                    "timestamp": "2025-06-09T10:30:00",
                    "reliability": 1.0
                }
            ]
        },
        "5min": {
            "meta": {
                "level": "5min",
                "analysis_level": "standard",
                "data_count": 2904
            },
            "structures": {
                "fenxing_count": 519,
                "bi_count": 518,
                "seg_count": 70,
                "zhongshu_count": 13
            },
            "dynamics": {
                "backchi_count": 0,
                "buy_sell_points_count": 159,
                "buy_points_count": 97,
                "sell_points_count": 62,
                "buy_sell_points": [
                    {
                        "id": "signal_0",
                        "name": "3sell",
                        "coord": [
                            "2025-04-07 10:10",
                            225.06
                        ],
                        "value": 225.06,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.22210428958867975,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 225,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-07 10:10",
                            "strength": 0.22210428958867975
                        }
                    },
                    {
                        "id": "signal_1",
                        "name": "3sell",
                        "coord": [
                            "2025-04-08 11:30",
                            218.89
                        ],
                        "value": 218.89,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.22429249918833294,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 279,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-04-07 13:45",
                            "end_time": "2025-04-08 11:30",
                            "strength": 0.22429249918833294
                        }
                    },
                    {
                        "id": "signal_2",
                        "name": "1buy",
                        "coord": [
                            "2025-04-14 09:35",
                            228.0
                        ],
                        "value": 228.0,
                        "type": "buy",
                        "point_level": 1,
                        "strength": 0.2110175166566196,
                        "reliability": 0.8,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 387,
                        "backchi_type": "bottom",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-10 13:30",
                            "end_time": "2025-04-14 09:35",
                            "strength": 0.18577243298040488
                        }
                    },
                    {
                        "id": "signal_3",
                        "name": "3sell",
                        "coord": [
                            "2025-04-14 09:35",
                            228.0
                        ],
                        "value": 228.0,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.18577243298040488,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 387,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-10 13:30",
                            "end_time": "2025-04-14 09:35",
                            "strength": 0.18577243298040488
                        }
                    },
                    {
                        "id": "signal_4",
                        "name": "3sell",
                        "coord": [
                            "2025-04-15 13:05",
                            228.86
                        ],
                        "value": 228.86,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15886825560375772,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 431,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-14 11:05",
                            "end_time": "2025-04-15 13:05",
                            "strength": 0.15886825560375772
                        }
                    },
                    {
                        "id": "signal_5",
                        "name": "2buy",
                        "coord": [
                            "2025-04-16 10:30",
                            221.62
                        ],
                        "value": 221.62,
                        "type": "buy",
                        "point_level": 2,
                        "strength": 0.19243194728229157,
                        "reliability": 0.7,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 455,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-15 13:05",
                            "end_time": "2025-04-16 10:30",
                            "strength": 0.19243194728229157
                        }
                    },
                    {
                        "id": "signal_6",
                        "name": "3sell",
                        "coord": [
                            "2025-04-16 10:30",
                            221.62
                        ],
                        "value": 221.62,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.19243194728229157,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 455,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-15 13:05",
                            "end_time": "2025-04-16 10:30",
                            "strength": 0.19243194728229157
                        }
                    },
                    {
                        "id": "signal_7",
                        "name": "1sell",
                        "coord": [
                            "2025-04-18 10:50",
                            223.66
                        ],
                        "value": 223.66,
                        "type": "sell",
                        "point_level": 1,
                        "strength": 0.27436702709027705,
                        "reliability": 0.8,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 519,
                        "backchi_type": "top",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-04-16 10:30",
                            "end_time": "2025-04-18 10:50",
                            "strength": 0.16275403298738164
                        }
                    },
                    {
                        "id": "signal_8",
                        "name": "3sell",
                        "coord": [
                            "2025-04-18 10:50",
                            223.66
                        ],
                        "value": 223.66,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.16275403298738164,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 519,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-04-16 10:30",
                            "end_time": "2025-04-18 10:50",
                            "strength": 0.16275403298738164
                        }
                    },
                    {
                        "id": "signal_9",
                        "name": "3sell",
                        "coord": [
                            "2025-04-21 14:05",
                            232.63
                        ],
                        "value": 232.63,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17855074926091638,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 560,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-04-18 10:50",
                            "end_time": "2025-04-21 14:05",
                            "strength": 0.17855074926091638
                        }
                    },
                    {
                        "id": "signal_10",
                        "name": "1buy",
                        "coord": [
                            "2025-04-22 10:55",
                            227.9
                        ],
                        "value": 227.9,
                        "type": "buy",
                        "point_level": 1,
                        "strength": 0.21538911003538574,
                        "reliability": 0.8,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 584,
                        "backchi_type": "bottom",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-21 14:05",
                            "end_time": "2025-04-22 10:55",
                            "strength": 0.15098420141478253
                        }
                    },
                    {
                        "id": "signal_11",
                        "name": "2sell",
                        "coord": [
                            "2025-04-23 10:30",
                            234.46
                        ],
                        "value": 234.46,
                        "type": "sell",
                        "point_level": 2,
                        "strength": 0.18792922266996415,
                        "reliability": 0.7,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 612,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-23 10:30",
                            "strength": 0.18792922266996415
                        }
                    },
                    {
                        "id": "signal_12",
                        "name": "3buy",
                        "coord": [
                            "2025-04-23 10:30",
                            234.46
                        ],
                        "value": 234.46,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.18792922266996415,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 612,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-23 10:30",
                            "strength": 0.18792922266996415
                        }
                    },
                    {
                        "id": "signal_13",
                        "name": "3sell",
                        "coord": [
                            "2025-04-24 13:10",
                            236.96
                        ],
                        "value": 236.96,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.1488117036621383,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 657,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-23 10:30",
                            "end_time": "2025-04-24 13:10",
                            "strength": 0.1488117036621383
                        }
                    },
                    {
                        "id": "signal_14",
                        "name": "2buy",
                        "coord": [
                            "2025-04-25 09:55",
                            235.15
                        ],
                        "value": 235.15,
                        "type": "buy",
                        "point_level": 2,
                        "strength": 0.16201715455293347,
                        "reliability": 0.7,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 674,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-24 13:10",
                            "end_time": "2025-04-25 09:55",
                            "strength": 0.16201715455293347
                        }
                    },
                    {
                        "id": "signal_15",
                        "name": "3buy",
                        "coord": [
                            "2025-04-25 09:55",
                            235.15
                        ],
                        "value": 235.15,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16201715455293347,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 674,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-24 13:10",
                            "end_time": "2025-04-25 09:55",
                            "strength": 0.16201715455293347
                        }
                    },
                    {
                        "id": "signal_16",
                        "name": "3buy",
                        "coord": [
                            "2025-04-25 09:55",
                            235.15
                        ],
                        "value": 235.15,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16201715455293347,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 674,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-04-24 13:10",
                            "end_time": "2025-04-25 09:55",
                            "strength": 0.16201715455293347
                        }
                    },
                    {
                        "id": "signal_17",
                        "name": "3sell",
                        "coord": [
                            "2025-04-29 13:45",
                            232.58
                        ],
                        "value": 232.58,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15639086716519418,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 755,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-04-29 13:45",
                            "strength": 0.15639086716519418
                        }
                    },
                    {
                        "id": "signal_18",
                        "name": "3sell",
                        "coord": [
                            "2025-04-29 13:45",
                            232.58
                        ],
                        "value": 232.58,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15639086716519418,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 755,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-04-29 13:45",
                            "strength": 0.15639086716519418
                        }
                    },
                    {
                        "id": "signal_19",
                        "name": "3buy",
                        "coord": [
                            "2025-05-07 10:10",
                            238.66
                        ],
                        "value": 238.66,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1916590726105405,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 844,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-06 13:05",
                            "end_time": "2025-05-07 10:10",
                            "strength": 0.1916590726105405
                        }
                    },
                    {
                        "id": "signal_20",
                        "name": "3buy",
                        "coord": [
                            "2025-05-07 10:10",
                            238.66
                        ],
                        "value": 238.66,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1916590726105405,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 844,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-06 13:05",
                            "end_time": "2025-05-07 10:10",
                            "strength": 0.1916590726105405
                        }
                    },
                    {
                        "id": "signal_21",
                        "name": "3buy",
                        "coord": [
                            "2025-05-09 09:45",
                            247.5
                        ],
                        "value": 247.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.18822335465831366,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 900,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-07 10:10",
                            "end_time": "2025-05-09 09:45",
                            "strength": 0.18822335465831366
                        }
                    },
                    {
                        "id": "signal_22",
                        "name": "3buy",
                        "coord": [
                            "2025-05-09 09:45",
                            247.5
                        ],
                        "value": 247.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.18822335465831366,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 900,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-07 10:10",
                            "end_time": "2025-05-09 09:45",
                            "strength": 0.18822335465831366
                        }
                    },
                    {
                        "id": "signal_23",
                        "name": "3sell",
                        "coord": [
                            "2025-05-09 14:40",
                            249.77
                        ],
                        "value": 249.77,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.16217564206773044,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 929,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-09 09:45",
                            "end_time": "2025-05-09 14:40",
                            "strength": 0.16217564206773044
                        }
                    },
                    {
                        "id": "signal_24",
                        "name": "3sell",
                        "coord": [
                            "2025-05-12 14:00",
                            256.81
                        ],
                        "value": 256.81,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.1858952645578451,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 954,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-09 14:40",
                            "end_time": "2025-05-12 14:00",
                            "strength": 0.1858952645578451
                        }
                    },
                    {
                        "id": "signal_25",
                        "name": "3buy",
                        "coord": [
                            "2025-05-22 10:30",
                            268.27
                        ],
                        "value": 268.27,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.21881339782080822,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1171,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-21 13:25",
                            "end_time": "2025-05-22 10:30",
                            "strength": 0.21881339782080822
                        }
                    },
                    {
                        "id": "signal_26",
                        "name": "3buy",
                        "coord": [
                            "2025-05-22 10:30",
                            268.27
                        ],
                        "value": 268.27,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.21881339782080822,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1171,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-21 13:25",
                            "end_time": "2025-05-22 10:30",
                            "strength": 0.21881339782080822
                        }
                    },
                    {
                        "id": "signal_27",
                        "name": "3buy",
                        "coord": [
                            "2025-05-22 10:30",
                            268.27
                        ],
                        "value": 268.27,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.21881339782080822,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1171,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-21 13:25",
                            "end_time": "2025-05-22 10:30",
                            "strength": 0.21881339782080822
                        }
                    },
                    {
                        "id": "signal_28",
                        "name": "3buy",
                        "coord": [
                            "2025-05-22 10:30",
                            268.27
                        ],
                        "value": 268.27,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.21881339782080822,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1171,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-21 13:25",
                            "end_time": "2025-05-22 10:30",
                            "strength": 0.21881339782080822
                        }
                    },
                    {
                        "id": "signal_29",
                        "name": "3buy",
                        "coord": [
                            "2025-05-22 10:30",
                            268.27
                        ],
                        "value": 268.27,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.21881339782080822,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1171,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-21 13:25",
                            "end_time": "2025-05-22 10:30",
                            "strength": 0.21881339782080822
                        }
                    },
                    {
                        "id": "signal_30",
                        "name": "3buy",
                        "coord": [
                            "2025-05-28 09:40",
                            257.5
                        ],
                        "value": 257.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.190727049814651,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1311,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-26 14:55",
                            "end_time": "2025-05-28 09:40",
                            "strength": 0.190727049814651
                        }
                    },
                    {
                        "id": "signal_31",
                        "name": "3buy",
                        "coord": [
                            "2025-05-28 09:40",
                            257.5
                        ],
                        "value": 257.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.190727049814651,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1311,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-26 14:55",
                            "end_time": "2025-05-28 09:40",
                            "strength": 0.190727049814651
                        }
                    },
                    {
                        "id": "signal_32",
                        "name": "3buy",
                        "coord": [
                            "2025-05-28 09:40",
                            257.5
                        ],
                        "value": 257.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.190727049814651,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1311,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-26 14:55",
                            "end_time": "2025-05-28 09:40",
                            "strength": 0.190727049814651
                        }
                    },
                    {
                        "id": "signal_33",
                        "name": "3buy",
                        "coord": [
                            "2025-05-28 09:40",
                            257.5
                        ],
                        "value": 257.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.190727049814651,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1311,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-26 14:55",
                            "end_time": "2025-05-28 09:40",
                            "strength": 0.190727049814651
                        }
                    },
                    {
                        "id": "signal_34",
                        "name": "3buy",
                        "coord": [
                            "2025-05-28 09:40",
                            257.5
                        ],
                        "value": 257.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.190727049814651,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1311,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-26 14:55",
                            "end_time": "2025-05-28 09:40",
                            "strength": 0.190727049814651
                        }
                    },
                    {
                        "id": "signal_35",
                        "name": "3sell",
                        "coord": [
                            "2025-05-28 13:30",
                            254.34
                        ],
                        "value": 254.34,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17135979887730507,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1333,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-28 09:40",
                            "end_time": "2025-05-28 13:30",
                            "strength": 0.17135979887730507
                        }
                    },
                    {
                        "id": "signal_36",
                        "name": "3sell",
                        "coord": [
                            "2025-05-28 13:30",
                            254.34
                        ],
                        "value": 254.34,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17135979887730507,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1333,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-28 09:40",
                            "end_time": "2025-05-28 13:30",
                            "strength": 0.17135979887730507
                        }
                    },
                    {
                        "id": "signal_37",
                        "name": "3buy",
                        "coord": [
                            "2025-05-29 10:15",
                            251.09
                        ],
                        "value": 251.09,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15877588859579356,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1355,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-29 10:15",
                            "strength": 0.15877588859579356
                        }
                    },
                    {
                        "id": "signal_38",
                        "name": "3buy",
                        "coord": [
                            "2025-05-29 10:15",
                            251.09
                        ],
                        "value": 251.09,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15877588859579356,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1355,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-29 10:15",
                            "strength": 0.15877588859579356
                        }
                    },
                    {
                        "id": "signal_39",
                        "name": "3buy",
                        "coord": [
                            "2025-05-29 10:15",
                            251.09
                        ],
                        "value": 251.09,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15877588859579356,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1355,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-29 10:15",
                            "strength": 0.15877588859579356
                        }
                    },
                    {
                        "id": "signal_40",
                        "name": "3buy",
                        "coord": [
                            "2025-05-29 10:15",
                            251.09
                        ],
                        "value": 251.09,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15877588859579356,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1355,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-29 10:15",
                            "strength": 0.15877588859579356
                        }
                    },
                    {
                        "id": "signal_41",
                        "name": "3sell",
                        "coord": [
                            "2025-05-29 13:10",
                            252.91
                        ],
                        "value": 252.91,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15414581071746766,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1369,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-29 10:15",
                            "end_time": "2025-05-29 13:10",
                            "strength": 0.15414581071746766
                        }
                    },
                    {
                        "id": "signal_42",
                        "name": "3sell",
                        "coord": [
                            "2025-05-29 13:10",
                            252.91
                        ],
                        "value": 252.91,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15414581071746766,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1369,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-29 10:15",
                            "end_time": "2025-05-29 13:10",
                            "strength": 0.15414581071746766
                        }
                    },
                    {
                        "id": "signal_43",
                        "name": "3sell",
                        "coord": [
                            "2025-05-29 13:10",
                            252.91
                        ],
                        "value": 252.91,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15414581071746766,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1369,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-29 10:15",
                            "end_time": "2025-05-29 13:10",
                            "strength": 0.15414581071746766
                        }
                    },
                    {
                        "id": "signal_44",
                        "name": "3buy",
                        "coord": [
                            "2025-05-30 11:00",
                            248.3
                        ],
                        "value": 248.3,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1736646123319919,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1398,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-29 13:10",
                            "end_time": "2025-05-30 11:00",
                            "strength": 0.1736646123319919
                        }
                    },
                    {
                        "id": "signal_45",
                        "name": "3buy",
                        "coord": [
                            "2025-05-30 11:00",
                            248.3
                        ],
                        "value": 248.3,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1736646123319919,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1398,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-29 13:10",
                            "end_time": "2025-05-30 11:00",
                            "strength": 0.1736646123319919
                        }
                    },
                    {
                        "id": "signal_46",
                        "name": "3buy",
                        "coord": [
                            "2025-05-30 11:00",
                            248.3
                        ],
                        "value": 248.3,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1736646123319919,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1398,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-29 13:10",
                            "end_time": "2025-05-30 11:00",
                            "strength": 0.1736646123319919
                        }
                    },
                    {
                        "id": "signal_47",
                        "name": "3buy",
                        "coord": [
                            "2025-05-30 11:00",
                            248.3
                        ],
                        "value": 248.3,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1736646123319919,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1398,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-05-29 13:10",
                            "end_time": "2025-05-30 11:00",
                            "strength": 0.1736646123319919
                        }
                    },
                    {
                        "id": "signal_48",
                        "name": "3buy",
                        "coord": [
                            "2025-05-30 14:15",
                            250.37
                        ],
                        "value": 250.37,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1522130007250635,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1415,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-30 11:00",
                            "end_time": "2025-05-30 14:15",
                            "strength": 0.1522130007250635
                        }
                    },
                    {
                        "id": "signal_49",
                        "name": "3buy",
                        "coord": [
                            "2025-05-30 14:15",
                            250.37
                        ],
                        "value": 250.37,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1522130007250635,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1415,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-30 11:00",
                            "end_time": "2025-05-30 14:15",
                            "strength": 0.1522130007250635
                        }
                    },
                    {
                        "id": "signal_50",
                        "name": "3buy",
                        "coord": [
                            "2025-05-30 14:15",
                            250.37
                        ],
                        "value": 250.37,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1522130007250635,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1415,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-30 11:00",
                            "end_time": "2025-05-30 14:15",
                            "strength": 0.1522130007250635
                        }
                    },
                    {
                        "id": "signal_51",
                        "name": "3buy",
                        "coord": [
                            "2025-05-30 14:15",
                            250.37
                        ],
                        "value": 250.37,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1522130007250635,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1415,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-30 11:00",
                            "end_time": "2025-05-30 14:15",
                            "strength": 0.1522130007250635
                        }
                    },
                    {
                        "id": "signal_52",
                        "name": "3sell",
                        "coord": [
                            "2025-06-03 11:30",
                            252.66
                        ],
                        "value": 252.66,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.19012041625332624,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1437,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-30 14:15",
                            "end_time": "2025-06-03 11:30",
                            "strength": 0.19012041625332624
                        }
                    },
                    {
                        "id": "signal_53",
                        "name": "3sell",
                        "coord": [
                            "2025-06-03 11:30",
                            252.66
                        ],
                        "value": 252.66,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.19012041625332624,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1437,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-30 14:15",
                            "end_time": "2025-06-03 11:30",
                            "strength": 0.19012041625332624
                        }
                    },
                    {
                        "id": "signal_54",
                        "name": "3sell",
                        "coord": [
                            "2025-06-03 11:30",
                            252.66
                        ],
                        "value": 252.66,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.19012041625332624,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1437,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-05-30 14:15",
                            "end_time": "2025-06-03 11:30",
                            "strength": 0.19012041625332624
                        }
                    },
                    {
                        "id": "signal_55",
                        "name": "3buy",
                        "coord": [
                            "2025-06-04 10:00",
                            250.7
                        ],
                        "value": 250.7,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.17267798888704386,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1460,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-03 11:30",
                            "end_time": "2025-06-04 10:00",
                            "strength": 0.17267798888704386
                        }
                    },
                    {
                        "id": "signal_56",
                        "name": "3buy",
                        "coord": [
                            "2025-06-04 10:00",
                            250.7
                        ],
                        "value": 250.7,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.17267798888704386,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1460,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-03 11:30",
                            "end_time": "2025-06-04 10:00",
                            "strength": 0.17267798888704386
                        }
                    },
                    {
                        "id": "signal_57",
                        "name": "3buy",
                        "coord": [
                            "2025-06-04 10:00",
                            250.7
                        ],
                        "value": 250.7,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.17267798888704386,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1460,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-03 11:30",
                            "end_time": "2025-06-04 10:00",
                            "strength": 0.17267798888704386
                        }
                    },
                    {
                        "id": "signal_58",
                        "name": "3buy",
                        "coord": [
                            "2025-06-04 10:00",
                            250.7
                        ],
                        "value": 250.7,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.17267798888704386,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1460,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-03 11:30",
                            "end_time": "2025-06-04 10:00",
                            "strength": 0.17267798888704386
                        }
                    },
                    {
                        "id": "signal_59",
                        "name": "3sell",
                        "coord": [
                            "2025-06-09 09:35",
                            246.53
                        ],
                        "value": 246.53,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15696381250407604,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1552,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-05 10:50",
                            "end_time": "2025-06-09 09:35",
                            "strength": 0.15696381250407604
                        }
                    },
                    {
                        "id": "signal_60",
                        "name": "3buy",
                        "coord": [
                            "2025-06-09 09:35",
                            246.53
                        ],
                        "value": 246.53,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15696381250407604,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1552,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-05 10:50",
                            "end_time": "2025-06-09 09:35",
                            "strength": 0.15696381250407604
                        }
                    },
                    {
                        "id": "signal_61",
                        "name": "3buy",
                        "coord": [
                            "2025-06-09 09:35",
                            246.53
                        ],
                        "value": 246.53,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15696381250407604,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1552,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-05 10:50",
                            "end_time": "2025-06-09 09:35",
                            "strength": 0.15696381250407604
                        }
                    },
                    {
                        "id": "signal_62",
                        "name": "3buy",
                        "coord": [
                            "2025-06-09 09:35",
                            246.53
                        ],
                        "value": 246.53,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15696381250407604,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1552,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-05 10:50",
                            "end_time": "2025-06-09 09:35",
                            "strength": 0.15696381250407604
                        }
                    },
                    {
                        "id": "signal_63",
                        "name": "3buy",
                        "coord": [
                            "2025-06-09 09:35",
                            246.53
                        ],
                        "value": 246.53,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15696381250407604,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1552,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-05 10:50",
                            "end_time": "2025-06-09 09:35",
                            "strength": 0.15696381250407604
                        }
                    },
                    {
                        "id": "signal_64",
                        "name": "3sell",
                        "coord": [
                            "2025-06-09 09:35",
                            246.53
                        ],
                        "value": 246.53,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15696381250407604,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1552,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-05 10:50",
                            "end_time": "2025-06-09 09:35",
                            "strength": 0.15696381250407604
                        }
                    },
                    {
                        "id": "signal_65",
                        "name": "3sell",
                        "coord": [
                            "2025-06-09 09:35",
                            246.53
                        ],
                        "value": 246.53,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15696381250407604,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1552,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-05 10:50",
                            "end_time": "2025-06-09 09:35",
                            "strength": 0.15696381250407604
                        }
                    },
                    {
                        "id": "signal_66",
                        "name": "3sell",
                        "coord": [
                            "2025-06-09 09:35",
                            246.53
                        ],
                        "value": 246.53,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15696381250407604,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1552,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-30 11:00",
                            "low": 251.09,
                            "high": 252.91,
                            "strength": 0.4393226193304781
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-05 10:50",
                            "end_time": "2025-06-09 09:35",
                            "strength": 0.15696381250407604
                        }
                    },
                    {
                        "id": "signal_67",
                        "name": "3buy",
                        "coord": [
                            "2025-06-10 14:20",
                            242.66
                        ],
                        "value": 242.66,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1435163870513815,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1607,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-10 10:30",
                            "end_time": "2025-06-10 14:20",
                            "strength": 0.1435163870513815
                        }
                    },
                    {
                        "id": "signal_68",
                        "name": "3buy",
                        "coord": [
                            "2025-06-10 14:20",
                            242.66
                        ],
                        "value": 242.66,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1435163870513815,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1607,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-10 10:30",
                            "end_time": "2025-06-10 14:20",
                            "strength": 0.1435163870513815
                        }
                    },
                    {
                        "id": "signal_69",
                        "name": "3buy",
                        "coord": [
                            "2025-06-10 14:20",
                            242.66
                        ],
                        "value": 242.66,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1435163870513815,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1607,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-10 10:30",
                            "end_time": "2025-06-10 14:20",
                            "strength": 0.1435163870513815
                        }
                    },
                    {
                        "id": "signal_70",
                        "name": "3buy",
                        "coord": [
                            "2025-06-10 14:20",
                            242.66
                        ],
                        "value": 242.66,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1435163870513815,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1607,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-10 10:30",
                            "end_time": "2025-06-10 14:20",
                            "strength": 0.1435163870513815
                        }
                    },
                    {
                        "id": "signal_71",
                        "name": "3buy",
                        "coord": [
                            "2025-06-12 10:50",
                            248.77
                        ],
                        "value": 248.77,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.18851552297817215,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1658,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-11 10:45",
                            "end_time": "2025-06-12 10:50",
                            "strength": 0.18851552297817215
                        }
                    },
                    {
                        "id": "signal_72",
                        "name": "3buy",
                        "coord": [
                            "2025-06-12 10:50",
                            248.77
                        ],
                        "value": 248.77,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.18851552297817215,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1658,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-11 10:45",
                            "end_time": "2025-06-12 10:50",
                            "strength": 0.18851552297817215
                        }
                    },
                    {
                        "id": "signal_73",
                        "name": "3buy",
                        "coord": [
                            "2025-06-12 10:50",
                            248.77
                        ],
                        "value": 248.77,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.18851552297817215,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1658,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-11 10:45",
                            "end_time": "2025-06-12 10:50",
                            "strength": 0.18851552297817215
                        }
                    },
                    {
                        "id": "signal_74",
                        "name": "3buy",
                        "coord": [
                            "2025-06-12 10:50",
                            248.77
                        ],
                        "value": 248.77,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.18851552297817215,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1658,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-11 10:45",
                            "end_time": "2025-06-12 10:50",
                            "strength": 0.18851552297817215
                        }
                    },
                    {
                        "id": "signal_75",
                        "name": "3buy",
                        "coord": [
                            "2025-06-13 11:00",
                            246.37
                        ],
                        "value": 246.37,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1692969367974267,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1688,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-12 10:50",
                            "end_time": "2025-06-13 11:00",
                            "strength": 0.1692969367974267
                        }
                    },
                    {
                        "id": "signal_76",
                        "name": "3buy",
                        "coord": [
                            "2025-06-13 11:00",
                            246.37
                        ],
                        "value": 246.37,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1692969367974267,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1688,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-12 10:50",
                            "end_time": "2025-06-13 11:00",
                            "strength": 0.1692969367974267
                        }
                    },
                    {
                        "id": "signal_77",
                        "name": "3buy",
                        "coord": [
                            "2025-06-13 11:00",
                            246.37
                        ],
                        "value": 246.37,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1692969367974267,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1688,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-12 10:50",
                            "end_time": "2025-06-13 11:00",
                            "strength": 0.1692969367974267
                        }
                    },
                    {
                        "id": "signal_78",
                        "name": "3buy",
                        "coord": [
                            "2025-06-13 11:00",
                            246.37
                        ],
                        "value": 246.37,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1692969367974267,
                        "reliability": 1.0,
                        "confirmed_higher": true,
                        "confirmed_lower": false,
                        "kline_index": 1688,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-12 10:50",
                            "end_time": "2025-06-13 11:00",
                            "strength": 0.1692969367974267
                        }
                    },
                    {
                        "id": "signal_79",
                        "name": "3sell",
                        "coord": [
                            "2025-06-17 11:25",
                            248.43
                        ],
                        "value": 248.43,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15913360392259215,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1760,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-17 09:40",
                            "end_time": "2025-06-17 11:25",
                            "strength": 0.15913360392259215
                        }
                    },
                    {
                        "id": "signal_80",
                        "name": "3buy",
                        "coord": [
                            "2025-06-17 11:25",
                            248.43
                        ],
                        "value": 248.43,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15913360392259215,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1760,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-17 09:40",
                            "end_time": "2025-06-17 11:25",
                            "strength": 0.15913360392259215
                        }
                    },
                    {
                        "id": "signal_81",
                        "name": "3buy",
                        "coord": [
                            "2025-06-17 11:25",
                            248.43
                        ],
                        "value": 248.43,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15913360392259215,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1760,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-17 09:40",
                            "end_time": "2025-06-17 11:25",
                            "strength": 0.15913360392259215
                        }
                    },
                    {
                        "id": "signal_82",
                        "name": "3buy",
                        "coord": [
                            "2025-06-17 11:25",
                            248.43
                        ],
                        "value": 248.43,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15913360392259215,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1760,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-17 09:40",
                            "end_time": "2025-06-17 11:25",
                            "strength": 0.15913360392259215
                        }
                    },
                    {
                        "id": "signal_83",
                        "name": "3buy",
                        "coord": [
                            "2025-06-17 11:25",
                            248.43
                        ],
                        "value": 248.43,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15913360392259215,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1760,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-17 09:40",
                            "end_time": "2025-06-17 11:25",
                            "strength": 0.15913360392259215
                        }
                    },
                    {
                        "id": "signal_84",
                        "name": "3sell",
                        "coord": [
                            "2025-06-17 11:25",
                            248.43
                        ],
                        "value": 248.43,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15913360392259215,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1760,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-17 09:40",
                            "end_time": "2025-06-17 11:25",
                            "strength": 0.15913360392259215
                        }
                    },
                    {
                        "id": "signal_85",
                        "name": "3sell",
                        "coord": [
                            "2025-06-17 11:25",
                            248.43
                        ],
                        "value": 248.43,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15913360392259215,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1760,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-17 09:40",
                            "end_time": "2025-06-17 11:25",
                            "strength": 0.15913360392259215
                        }
                    },
                    {
                        "id": "signal_86",
                        "name": "3sell",
                        "coord": [
                            "2025-06-17 11:25",
                            248.43
                        ],
                        "value": 248.43,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15913360392259215,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1760,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-30 11:00",
                            "low": 251.09,
                            "high": 252.91,
                            "strength": 0.4393226193304781
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-17 09:40",
                            "end_time": "2025-06-17 11:25",
                            "strength": 0.15913360392259215
                        }
                    },
                    {
                        "id": "signal_87",
                        "name": "3sell",
                        "coord": [
                            "2025-06-17 11:25",
                            248.43
                        ],
                        "value": 248.43,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15913360392259215,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1760,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-30 14:15",
                            "end_time": "2025-06-09 09:35",
                            "low": 250.44,
                            "high": 253.3,
                            "strength": 0.4520117572600187
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-17 09:40",
                            "end_time": "2025-06-17 11:25",
                            "strength": 0.15913360392259215
                        }
                    },
                    {
                        "id": "signal_88",
                        "name": "3buy",
                        "coord": [
                            "2025-06-20 09:50",
                            243.12
                        ],
                        "value": 243.12,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1619688567190183,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1853,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-18 10:50",
                            "end_time": "2025-06-20 09:50",
                            "strength": 0.1619688567190183
                        }
                    },
                    {
                        "id": "signal_89",
                        "name": "3buy",
                        "coord": [
                            "2025-06-20 09:50",
                            243.12
                        ],
                        "value": 243.12,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1619688567190183,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1853,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-18 10:50",
                            "end_time": "2025-06-20 09:50",
                            "strength": 0.1619688567190183
                        }
                    },
                    {
                        "id": "signal_90",
                        "name": "3buy",
                        "coord": [
                            "2025-06-20 09:50",
                            243.12
                        ],
                        "value": 243.12,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1619688567190183,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1853,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-18 10:50",
                            "end_time": "2025-06-20 09:50",
                            "strength": 0.1619688567190183
                        }
                    },
                    {
                        "id": "signal_91",
                        "name": "3buy",
                        "coord": [
                            "2025-06-20 09:50",
                            243.12
                        ],
                        "value": 243.12,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1619688567190183,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1853,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-18 10:50",
                            "end_time": "2025-06-20 09:50",
                            "strength": 0.1619688567190183
                        }
                    },
                    {
                        "id": "signal_92",
                        "name": "3sell",
                        "coord": [
                            "2025-06-23 13:40",
                            238.5
                        ],
                        "value": 238.5,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15678627496239136,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1902,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-20 13:20",
                            "end_time": "2025-06-23 13:40",
                            "strength": 0.15678627496239136
                        }
                    },
                    {
                        "id": "signal_93",
                        "name": "3sell",
                        "coord": [
                            "2025-06-23 13:40",
                            238.5
                        ],
                        "value": 238.5,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15678627496239136,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1902,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-20 13:20",
                            "end_time": "2025-06-23 13:40",
                            "strength": 0.15678627496239136
                        }
                    },
                    {
                        "id": "signal_94",
                        "name": "3sell",
                        "coord": [
                            "2025-06-23 13:40",
                            238.5
                        ],
                        "value": 238.5,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15678627496239136,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1902,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-20 13:20",
                            "end_time": "2025-06-23 13:40",
                            "strength": 0.15678627496239136
                        }
                    },
                    {
                        "id": "signal_95",
                        "name": "3sell",
                        "coord": [
                            "2025-06-23 13:40",
                            238.5
                        ],
                        "value": 238.5,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15678627496239136,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1902,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-30 11:00",
                            "low": 251.09,
                            "high": 252.91,
                            "strength": 0.4393226193304781
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-20 13:20",
                            "end_time": "2025-06-23 13:40",
                            "strength": 0.15678627496239136
                        }
                    },
                    {
                        "id": "signal_96",
                        "name": "3sell",
                        "coord": [
                            "2025-06-23 13:40",
                            238.5
                        ],
                        "value": 238.5,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15678627496239136,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1902,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-30 14:15",
                            "end_time": "2025-06-09 09:35",
                            "low": 250.44,
                            "high": 253.3,
                            "strength": 0.4520117572600187
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-20 13:20",
                            "end_time": "2025-06-23 13:40",
                            "strength": 0.15678627496239136
                        }
                    },
                    {
                        "id": "signal_97",
                        "name": "3sell",
                        "coord": [
                            "2025-06-23 13:40",
                            238.5
                        ],
                        "value": 238.5,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15678627496239136,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1902,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-06-10 14:20",
                            "end_time": "2025-06-13 11:00",
                            "low": 248.77,
                            "high": 250.59,
                            "strength": 0.4491952680771447
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-20 13:20",
                            "end_time": "2025-06-23 13:40",
                            "strength": 0.15678627496239136
                        }
                    },
                    {
                        "id": "signal_98",
                        "name": "3sell",
                        "coord": [
                            "2025-06-24 13:15",
                            246.35
                        ],
                        "value": 246.35,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.20103277300576455,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1934,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-23 13:40",
                            "end_time": "2025-06-24 13:15",
                            "strength": 0.20103277300576455
                        }
                    },
                    {
                        "id": "signal_99",
                        "name": "3sell",
                        "coord": [
                            "2025-06-24 13:15",
                            246.35
                        ],
                        "value": 246.35,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.20103277300576455,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1934,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-23 13:40",
                            "end_time": "2025-06-24 13:15",
                            "strength": 0.20103277300576455
                        }
                    },
                    {
                        "id": "signal_100",
                        "name": "3sell",
                        "coord": [
                            "2025-06-24 13:15",
                            246.35
                        ],
                        "value": 246.35,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.20103277300576455,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1934,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-23 13:40",
                            "end_time": "2025-06-24 13:15",
                            "strength": 0.20103277300576455
                        }
                    },
                    {
                        "id": "signal_101",
                        "name": "3sell",
                        "coord": [
                            "2025-06-24 13:15",
                            246.35
                        ],
                        "value": 246.35,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.20103277300576455,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1934,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-30 11:00",
                            "low": 251.09,
                            "high": 252.91,
                            "strength": 0.4393226193304781
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-23 13:40",
                            "end_time": "2025-06-24 13:15",
                            "strength": 0.20103277300576455
                        }
                    },
                    {
                        "id": "signal_102",
                        "name": "3sell",
                        "coord": [
                            "2025-06-24 13:15",
                            246.35
                        ],
                        "value": 246.35,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.20103277300576455,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1934,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-30 14:15",
                            "end_time": "2025-06-09 09:35",
                            "low": 250.44,
                            "high": 253.3,
                            "strength": 0.4520117572600187
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-23 13:40",
                            "end_time": "2025-06-24 13:15",
                            "strength": 0.20103277300576455
                        }
                    },
                    {
                        "id": "signal_103",
                        "name": "3sell",
                        "coord": [
                            "2025-06-24 13:15",
                            246.35
                        ],
                        "value": 246.35,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.20103277300576455,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1934,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-06-10 14:20",
                            "end_time": "2025-06-13 11:00",
                            "low": 248.77,
                            "high": 250.59,
                            "strength": 0.4491952680771447
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-06-23 13:40",
                            "end_time": "2025-06-24 13:15",
                            "strength": 0.20103277300576455
                        }
                    },
                    {
                        "id": "signal_104",
                        "name": "3sell",
                        "coord": [
                            "2025-06-25 13:40",
                            252.79
                        ],
                        "value": 252.79,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.16277648671321068,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1972,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-24 13:15",
                            "end_time": "2025-06-25 13:40",
                            "strength": 0.16277648671321068
                        }
                    },
                    {
                        "id": "signal_105",
                        "name": "3sell",
                        "coord": [
                            "2025-06-25 13:40",
                            252.79
                        ],
                        "value": 252.79,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.16277648671321068,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1972,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-24 13:15",
                            "end_time": "2025-06-25 13:40",
                            "strength": 0.16277648671321068
                        }
                    },
                    {
                        "id": "signal_106",
                        "name": "3sell",
                        "coord": [
                            "2025-06-25 13:40",
                            252.79
                        ],
                        "value": 252.79,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.16277648671321068,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1972,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-24 13:15",
                            "end_time": "2025-06-25 13:40",
                            "strength": 0.16277648671321068
                        }
                    },
                    {
                        "id": "signal_107",
                        "name": "3sell",
                        "coord": [
                            "2025-06-25 13:40",
                            252.79
                        ],
                        "value": 252.79,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.16277648671321068,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1972,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-30 11:00",
                            "low": 251.09,
                            "high": 252.91,
                            "strength": 0.4393226193304781
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-24 13:15",
                            "end_time": "2025-06-25 13:40",
                            "strength": 0.16277648671321068
                        }
                    },
                    {
                        "id": "signal_108",
                        "name": "3sell",
                        "coord": [
                            "2025-06-25 13:40",
                            252.79
                        ],
                        "value": 252.79,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.16277648671321068,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1972,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-30 14:15",
                            "end_time": "2025-06-09 09:35",
                            "low": 250.44,
                            "high": 253.3,
                            "strength": 0.4520117572600187
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-24 13:15",
                            "end_time": "2025-06-25 13:40",
                            "strength": 0.16277648671321068
                        }
                    },
                    {
                        "id": "signal_109",
                        "name": "3sell",
                        "coord": [
                            "2025-06-25 13:40",
                            252.79
                        ],
                        "value": 252.79,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.16277648671321068,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 1972,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-06-10 14:20",
                            "end_time": "2025-06-13 11:00",
                            "low": 248.77,
                            "high": 250.59,
                            "strength": 0.4491952680771447
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-24 13:15",
                            "end_time": "2025-06-25 13:40",
                            "strength": 0.16277648671321068
                        }
                    },
                    {
                        "id": "signal_110",
                        "name": "3buy",
                        "coord": [
                            "2025-06-27 10:00",
                            257.31
                        ],
                        "value": 257.31,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1652686149620624,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2016,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-25 13:40",
                            "end_time": "2025-06-27 10:00",
                            "strength": 0.1652686149620624
                        }
                    },
                    {
                        "id": "signal_111",
                        "name": "3buy",
                        "coord": [
                            "2025-06-27 10:00",
                            257.31
                        ],
                        "value": 257.31,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1652686149620624,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2016,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-25 13:40",
                            "end_time": "2025-06-27 10:00",
                            "strength": 0.1652686149620624
                        }
                    },
                    {
                        "id": "signal_112",
                        "name": "3buy",
                        "coord": [
                            "2025-06-27 10:00",
                            257.31
                        ],
                        "value": 257.31,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1652686149620624,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2016,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-25 13:40",
                            "end_time": "2025-06-27 10:00",
                            "strength": 0.1652686149620624
                        }
                    },
                    {
                        "id": "signal_113",
                        "name": "3buy",
                        "coord": [
                            "2025-06-27 10:00",
                            257.31
                        ],
                        "value": 257.31,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.1652686149620624,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2016,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-25 13:40",
                            "end_time": "2025-06-27 10:00",
                            "strength": 0.1652686149620624
                        }
                    },
                    {
                        "id": "signal_114",
                        "name": "3sell",
                        "coord": [
                            "2025-07-01 10:20",
                            250.03
                        ],
                        "value": 250.03,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.19649932329743092,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2082,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-27 10:00",
                            "end_time": "2025-07-01 10:20",
                            "strength": 0.19649932329743092
                        }
                    },
                    {
                        "id": "signal_115",
                        "name": "3sell",
                        "coord": [
                            "2025-07-01 10:20",
                            250.03
                        ],
                        "value": 250.03,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.19649932329743092,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2082,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-27 10:00",
                            "end_time": "2025-07-01 10:20",
                            "strength": 0.19649932329743092
                        }
                    },
                    {
                        "id": "signal_116",
                        "name": "3sell",
                        "coord": [
                            "2025-07-01 10:20",
                            250.03
                        ],
                        "value": 250.03,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.19649932329743092,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2082,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-06-27 10:00",
                            "end_time": "2025-07-01 10:20",
                            "strength": 0.19649932329743092
                        }
                    },
                    {
                        "id": "signal_117",
                        "name": "3sell",
                        "coord": [
                            "2025-07-04 09:40",
                            260.98
                        ],
                        "value": 260.98,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17989126522547955,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2174,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-07-02 14:00",
                            "end_time": "2025-07-04 09:40",
                            "strength": 0.17989126522547955
                        }
                    },
                    {
                        "id": "signal_118",
                        "name": "3sell",
                        "coord": [
                            "2025-07-04 09:40",
                            260.98
                        ],
                        "value": 260.98,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17989126522547955,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2174,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-07-02 14:00",
                            "end_time": "2025-07-04 09:40",
                            "strength": 0.17989126522547955
                        }
                    },
                    {
                        "id": "signal_119",
                        "name": "3sell",
                        "coord": [
                            "2025-07-04 09:40",
                            260.98
                        ],
                        "value": 260.98,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17989126522547955,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2174,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-07-02 14:00",
                            "end_time": "2025-07-04 09:40",
                            "strength": 0.17989126522547955
                        }
                    },
                    {
                        "id": "signal_120",
                        "name": "3sell",
                        "coord": [
                            "2025-07-04 09:40",
                            260.98
                        ],
                        "value": 260.98,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17989126522547955,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2174,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-07-02 14:00",
                            "end_time": "2025-07-04 09:40",
                            "strength": 0.17989126522547955
                        }
                    },
                    {
                        "id": "signal_121",
                        "name": "3sell",
                        "coord": [
                            "2025-07-04 09:40",
                            260.98
                        ],
                        "value": 260.98,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17989126522547955,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2174,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "up",
                            "start_time": "2025-07-02 14:00",
                            "end_time": "2025-07-04 09:40",
                            "strength": 0.17989126522547955
                        }
                    },
                    {
                        "id": "signal_122",
                        "name": "1buy",
                        "coord": [
                            "2025-07-08 10:35",
                            263.5
                        ],
                        "value": 263.5,
                        "type": "buy",
                        "point_level": 1,
                        "strength": 0.2562829704577464,
                        "reliability": 0.8,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2240,
                        "backchi_type": "bottom",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-04 14:55",
                            "end_time": "2025-07-08 10:35",
                            "strength": 0.14613989302982827
                        }
                    },
                    {
                        "id": "signal_123",
                        "name": "3buy",
                        "coord": [
                            "2025-07-08 10:35",
                            263.5
                        ],
                        "value": 263.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.14613989302982827,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2240,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-04 14:55",
                            "end_time": "2025-07-08 10:35",
                            "strength": 0.14613989302982827
                        }
                    },
                    {
                        "id": "signal_124",
                        "name": "3buy",
                        "coord": [
                            "2025-07-08 10:35",
                            263.5
                        ],
                        "value": 263.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.14613989302982827,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2240,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-04 14:55",
                            "end_time": "2025-07-08 10:35",
                            "strength": 0.14613989302982827
                        }
                    },
                    {
                        "id": "signal_125",
                        "name": "3buy",
                        "coord": [
                            "2025-07-08 10:35",
                            263.5
                        ],
                        "value": 263.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.14613989302982827,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2240,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-04 14:55",
                            "end_time": "2025-07-08 10:35",
                            "strength": 0.14613989302982827
                        }
                    },
                    {
                        "id": "signal_126",
                        "name": "3buy",
                        "coord": [
                            "2025-07-08 10:35",
                            263.5
                        ],
                        "value": 263.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.14613989302982827,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2240,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-04 14:55",
                            "end_time": "2025-07-08 10:35",
                            "strength": 0.14613989302982827
                        }
                    },
                    {
                        "id": "signal_127",
                        "name": "3buy",
                        "coord": [
                            "2025-07-08 10:35",
                            263.5
                        ],
                        "value": 263.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.14613989302982827,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2240,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-04 14:55",
                            "end_time": "2025-07-08 10:35",
                            "strength": 0.14613989302982827
                        }
                    },
                    {
                        "id": "signal_128",
                        "name": "3buy",
                        "coord": [
                            "2025-07-08 10:35",
                            263.5
                        ],
                        "value": 263.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.14613989302982827,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2240,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-30 11:00",
                            "low": 251.09,
                            "high": 252.91,
                            "strength": 0.4393226193304781
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-04 14:55",
                            "end_time": "2025-07-08 10:35",
                            "strength": 0.14613989302982827
                        }
                    },
                    {
                        "id": "signal_129",
                        "name": "3buy",
                        "coord": [
                            "2025-07-08 10:35",
                            263.5
                        ],
                        "value": 263.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.14613989302982827,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2240,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-30 14:15",
                            "end_time": "2025-06-09 09:35",
                            "low": 250.44,
                            "high": 253.3,
                            "strength": 0.4520117572600187
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-04 14:55",
                            "end_time": "2025-07-08 10:35",
                            "strength": 0.14613989302982827
                        }
                    },
                    {
                        "id": "signal_130",
                        "name": "3buy",
                        "coord": [
                            "2025-07-08 10:35",
                            263.5
                        ],
                        "value": 263.5,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.14613989302982827,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2240,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-06-10 14:20",
                            "end_time": "2025-06-13 11:00",
                            "low": 248.77,
                            "high": 250.59,
                            "strength": 0.4491952680771447
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-04 14:55",
                            "end_time": "2025-07-08 10:35",
                            "strength": 0.14613989302982827
                        }
                    },
                    {
                        "id": "signal_131",
                        "name": "3buy",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_132",
                        "name": "3buy",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_133",
                        "name": "3buy",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_134",
                        "name": "3buy",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_135",
                        "name": "3buy",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_136",
                        "name": "3buy",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_137",
                        "name": "3sell",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_138",
                        "name": "3buy",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-30 11:00",
                            "low": 251.09,
                            "high": 252.91,
                            "strength": 0.4393226193304781
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_139",
                        "name": "3buy",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-30 14:15",
                            "end_time": "2025-06-09 09:35",
                            "low": 250.44,
                            "high": 253.3,
                            "strength": 0.4520117572600187
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_140",
                        "name": "3buy",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-06-10 14:20",
                            "end_time": "2025-06-13 11:00",
                            "low": 248.77,
                            "high": 250.59,
                            "strength": 0.4491952680771447
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_141",
                        "name": "3buy",
                        "coord": [
                            "2025-07-09 14:35",
                            272.0
                        ],
                        "value": 272.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.16011038117476548,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2298,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-06-25 13:40",
                            "end_time": "2025-07-04 09:40",
                            "low": 251.55,
                            "high": 257.31,
                            "strength": 0.4774989066502543
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-08 13:55",
                            "end_time": "2025-07-09 14:35",
                            "strength": 0.16011038117476548
                        }
                    },
                    {
                        "id": "signal_142",
                        "name": "2buy",
                        "coord": [
                            "2025-07-10 10:55",
                            268.5
                        ],
                        "value": 268.5,
                        "type": "buy",
                        "point_level": 2,
                        "strength": 0.1832001629450803,
                        "reliability": 0.7,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2317,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-09 14:35",
                            "end_time": "2025-07-10 10:55",
                            "strength": 0.1832001629450803
                        }
                    },
                    {
                        "id": "signal_143",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-03-25 14:35",
                            "end_time": "2025-03-31 13:50",
                            "low": 256.67,
                            "high": 257.98,
                            "strength": 0.4559583423343753
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_144",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-02 15:00",
                            "end_time": "2025-04-14 09:35",
                            "low": 216.8,
                            "high": 225.0,
                            "strength": 0.5410044852871568
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_145",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-14 09:35",
                            "end_time": "2025-04-21 14:05",
                            "low": 223.66,
                            "high": 226.47,
                            "strength": 0.4962836758379108
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_146",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-22 10:55",
                            "end_time": "2025-04-25 09:55",
                            "low": 235.15,
                            "high": 237.48,
                            "strength": 0.44622051972118965
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_147",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-04-28 10:25",
                            "end_time": "2025-05-07 10:10",
                            "low": 231.7,
                            "high": 235.58,
                            "strength": 0.46289912616765
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_148",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-12 14:00",
                            "end_time": "2025-05-20 13:35",
                            "low": 260.42,
                            "high": 262.87,
                            "strength": 0.44807850496353147
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_149",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_150",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-28 13:30",
                            "end_time": "2025-05-30 11:00",
                            "low": 251.09,
                            "high": 252.91,
                            "strength": 0.4393226193304781
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_151",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-30 14:15",
                            "end_time": "2025-06-09 09:35",
                            "low": 250.44,
                            "high": 253.3,
                            "strength": 0.4520117572600187
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_152",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-06-10 14:20",
                            "end_time": "2025-06-13 11:00",
                            "low": 248.77,
                            "high": 250.59,
                            "strength": 0.4491952680771447
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_153",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-06-25 13:40",
                            "end_time": "2025-07-04 09:40",
                            "low": 251.55,
                            "high": 257.31,
                            "strength": 0.4774989066502543
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_154",
                        "name": "3buy",
                        "coord": [
                            "2025-07-14 10:20",
                            268.0
                        ],
                        "value": 268.0,
                        "type": "buy",
                        "point_level": 3,
                        "strength": 0.15254172487918394,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2382,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": 90,
                        "itemStyle": {
                            "color": "#4caf50"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-07-04 09:40",
                            "end_time": "2025-07-09 14:35",
                            "low": 262.1,
                            "high": 266.05,
                            "strength": 0.4604659997790265
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-11 14:20",
                            "end_time": "2025-07-14 10:20",
                            "strength": 0.15254172487918394
                        }
                    },
                    {
                        "id": "signal_155",
                        "name": "3sell",
                        "coord": [
                            "2025-07-16 10:40",
                            265.14
                        ],
                        "value": 265.14,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.15371443332710666,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2460,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-15 10:40",
                            "end_time": "2025-07-16 10:40",
                            "strength": 0.15371443332710666
                        }
                    },
                    {
                        "id": "signal_156",
                        "name": "3sell",
                        "coord": [
                            "2025-07-18 13:35",
                            269.3
                        ],
                        "value": 269.3,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17361043134977472,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2529,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-05-20 13:35",
                            "end_time": "2025-05-26 14:55",
                            "low": 268.27,
                            "high": 272.78,
                            "strength": 0.49451840776214434
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-17 14:25",
                            "end_time": "2025-07-18 13:35",
                            "strength": 0.17361043134977472
                        }
                    },
                    {
                        "id": "signal_157",
                        "name": "3sell",
                        "coord": [
                            "2025-07-18 13:35",
                            269.3
                        ],
                        "value": 269.3,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17361043134977472,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2529,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-07-09 14:35",
                            "end_time": "2025-07-14 10:20",
                            "low": 270.1,
                            "high": 271.87,
                            "strength": 0.4621467675644607
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-17 14:25",
                            "end_time": "2025-07-18 13:35",
                            "strength": 0.17361043134977472
                        }
                    },
                    {
                        "id": "signal_158",
                        "name": "3sell",
                        "coord": [
                            "2025-07-18 13:35",
                            269.3
                        ],
                        "value": 269.3,
                        "type": "sell",
                        "point_level": 3,
                        "strength": 0.17361043134977472,
                        "reliability": 0.9,
                        "confirmed_higher": false,
                        "confirmed_lower": false,
                        "kline_index": 2529,
                        "backchi_type": "none",
                        "symbol": "arrow",
                        "symbolSize": 12,
                        "symbolRotate": -90,
                        "itemStyle": {
                            "color": "#f44336"
                        },
                        "related_zhongshu": {
                            "start_time": "2025-07-09 14:35",
                            "end_time": "2025-07-14 10:20",
                            "low": 270.1,
                            "high": 271.87,
                            "strength": 0.4621467675644607
                        },
                        "related_seg": {
                            "direction": "down",
                            "start_time": "2025-07-17 14:25",
                            "end_time": "2025-07-18 13:35",
                            "strength": 0.17361043134977472
                        }
                    }
                ],
                "backchi": []
            },
            "evaluation": {
                "trend_direction": null,
                "trend_strength": 0.0,
                "risk_level": 0.0,
                "confidence_score": 0.0,
                "recommended_action": null,
                "level_consistency_score": 0.12578616352201258
            },
            "latest_signals": [
                {
                    "type": "三类卖点",
                    "price": 269.3,
                    "timestamp": "2025-07-18T13:35:00",
                    "reliability": 0.9
                },
                {
                    "type": "三类卖点",
                    "price": 269.3,
                    "timestamp": "2025-07-18T13:35:00",
                    "reliability": 0.9
                },
                {
                    "type": "三类卖点",
                    "price": 269.3,
                    "timestamp": "2025-07-18T13:35:00",
                    "reliability": 0.9
                }
            ]
        }
    },
    "comparison": {
        "level_consistency": {
            "daily": 0.0,
            "30min": 1.0,
            "5min": 0.12578616352201258
        },
        "signal_confirmation": {
            "daily_vs_30min": 0.0,
            "daily_vs_5min": 0.0,
            "30min_vs_5min": 0.0
        },
        "trend_alignment": {}
    }
}