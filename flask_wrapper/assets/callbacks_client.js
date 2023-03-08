window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // Update frame of video
        positionUpdate: function(nclicks, nclicks2, nclicks3, nclicks4) {
            // console.log(window.dash_clientside.callback_context.triggered[0].prop_id)
            if (window.dash_clientside.callback_context.triggered[0].prop_id === 'top_pos_button.n_clicks') {

                // console.log(nclicks)
                const top_pos = document.getElementById('top_pos');
                const top_index = top_pos.innerText;
                if (nclicks > 0) {
                    return top_index;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'impact_pos_button.n_clicks') {
                // console.log(nclicks2)
                    const impact_pos = document.getElementById('impact_pos');
                    const impact_index = impact_pos.innerText;
                    if (nclicks2 > 0) {
                        return impact_index;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'end_pos_button.n_clicks') {
                const end_pos = document.getElementById('end_pos');
                const end_index = end_pos.innerText;
                if (nclicks3 > 0) {
                    return end_index;
                }
            }

            else {
                const setup_pos = document.getElementById('setup_pos');
                const setup_index = setup_pos.innerText;
                if (nclicks4 > 0) {
                    return setup_index;
                }
            }

        },

        // Update the vertical line on the sequence plot
        verticalLine: function(currentTime) {

            // Get the DOM element of the Plotly graph
            var graphDiv = document.getElementById('sequence');

            Plotly.update(
                graphDiv,
                        {
                            'shapes[0]': {
                                x0: currentTime,
                                x1: currentTime
                    }
                }
            )

        }

    }
});