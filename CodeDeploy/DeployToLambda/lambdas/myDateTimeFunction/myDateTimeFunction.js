'use strict';

exports.handler = function (event, context, callback) {

    if (event.body) {
        event = JSON.parse(event.body);
    }

    var sc; // Status code
    var result = ""; // Response payload

    switch (event.option) {
        case "date":
            switch (event.period) {
                case "yesterday":
                    result = setDateResult("yesterday");
                    sc = 200;
                    break;
                case "today":
                    result = setDateResult();
                    sc = 200;
                    break;
                case "tomorrow":
                    result = setDateResult("tomorrow");
                    sc = 200;
                    break;
                default:
                    result = {
                        "error": "Must specify 'yesterday', 'today', or 'tomorrow'."
                    };
                    sc = 400;
                    break;
            }
            break;

        /*      Later in this tutorial, you update this function by uncommenting 
                this section. The framework created by AWS SAM detects the update 
                and triggers a deployment by CodeDeploy. The deployment shifts 
                production traffic to the updated version of this function.
                
                case "time":
                var d = new Date();
                var h = d.getHours();
                var mi = d.getMinutes();
                var s = d.getSeconds();
        
                result = {
                  "hour": h,
                  "minute": mi,
                  "second": s
                };
                sc = 200;
                break;
        */
        default:
            result = {
                "error": "Must specify 'date' or 'time'."
            };
            sc = 400;
            break;
    }

    const response = {
        statusCode: sc,
        headers: { "Content-type": "application/json" },
        body: JSON.stringify(result)
    };

    callback(null, response);

    function setDateResult(option) {

        var d = new Date(); // Today
        var mo; // Month
        var da; // Day
        var y; // Year

        switch (option) {
            case "yesterday":
                d.setDate(d.getDate() - 1);
                break;
            case "tomorrow":
                d.setDate(d.getDate() + 1);
                break;
            default:
                break;
        }

        mo = d.getMonth() + 1; // Months are zero offset (0-11)
        da = d.getDate();
        y = d.getFullYear();

        result = {
            "month": mo,
            "day": da,
            "year": y
        };

        return result;
    }
};