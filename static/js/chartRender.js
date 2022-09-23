function getRandomColor() {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

async function payroll() {

    try {
        var xValues = new Array();
        var payrollValues = new Array();
        var overtimeValues = new Array();
        var barColors = new Array();
        const response = await axios.get(`/payrollStatistic`);
        const results = response.data;

        results.map((values) => {
            xValues.push(
                values.firstname
            );
            payrollValues.push(
                values.payrollValues
            );
            overtimeValues.push(
                values.overtimeValues
            );
            barColors.push(
                getRandomColor()
            )
        });
        xValues.push('');
        payrollValues.push('');
        overtimeValues.push('');

        var data = {
            labels: xValues,
            datasets: [
                {
                    label: 'Payroll',
                    data: payrollValues,
                    backgroundColor: "#caf270"
                },
                {
                    label: 'Overtime',
                    data: overtimeValues,
                    backgroundColor: "#45c490"
                }
            ]

        };

        const config = {
          type: 'bar',
          data: data
        };

        new Chart("payrollchart", config);

    } catch (errors) {
        console.error(errors);
    }

}

async function annualLeave() {

    try {
        var xValues = new Array();
        var annualDays = new Array();
        var sickDays = new Array();
        var unpaidDays = new Array();
        var barColors = new Array();
        const response = await axios.get(`/annualLeaveStatistic`);
        const results = response.data;

        results.map((values) => {
            xValues.push(
                values.firstname
            );
            annualDays.push(
                values.annualDays
            );
            sickDays.push(
                values.sickDays
            );
            unpaidDays.push(
                values.unpaidDays
            );
            barColors.push(
                getRandomColor()
            )
        });
        xValues.push('');
        annualDays.push('');
        sickDays.push('');
        unpaidDays.push('');

        var data = {
            labels: xValues,
            datasets: [
                {
                    label: 'Annual',
                    data: annualDays,
                    backgroundColor: "#2e5468"
                },
                {
                    label: 'Sick',
                    data: sickDays,
                    backgroundColor: "#45c490"
                },
                {
                    label: 'Unpaid',
                    data: unpaidDays,
                    backgroundColor: "#008d93"
                }
            ]

        };

        const config = {
          type: 'bar',
          data: data
        };

        new Chart("annualchart", config);

    } catch (errors) {
        console.error(errors);
    }

}



function renderReport() {
    payroll();
    annualLeave();

}