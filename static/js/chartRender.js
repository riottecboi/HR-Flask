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
        var yValues = new Array();
        var barColors = new Array();
        const response = await axios.get(`/payrollStatistic`);
        const results = response.data;

        results.map((values) => {
            xValues.push(
                values.firstname
            );
            yValues.push(
                values.payroll
            );
            barColors.push(
                getRandomColor()
            )
        });
        xValues.push('');
        yValues.push('');

        var data = {
            labels: xValues,
            datasets: [{
                label: 'Payroll Bar Chart',
                data: yValues,
                backgroundColor: barColors
            }]

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
        var yValues = new Array();
        var barColors = new Array();
        const response = await axios.get(`/annualLeaveStatistic`);
        const results = response.data;

        results.map((values) => {
            xValues.push(
                values.firstname
            );
            yValues.push(
                values.dayused
            );
            barColors.push(
                getRandomColor()
            )
        });
        xValues.push('');
        yValues.push('');

        var data = {
            labels: xValues,
            datasets: [{
                label: 'Total Leave Bar Chart',
                data: yValues,
                backgroundColor: barColors
            }]

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