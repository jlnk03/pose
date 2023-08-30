import {Card, LineChart, Title} from "@tremor/react";


function LinePlot({yValues, title}) {


    const chartDataFromYValues = yValues.map((value, index) => ({
        index: index,
        value: value
    }));


    return (
        <>
            <Card>
                <Title>{title}</Title>
                <LineChart
                    className="mt-6"
                    data={chartDataFromYValues}
                    index="index"
                    categories={["value"]}
                    colors={["emerald"]}
                    yAxisWidth={40}
                />

            </Card>
        </>
    );
}

export default LinePlot;
