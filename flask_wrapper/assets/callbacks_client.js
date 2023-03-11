window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // Update frame of video
        positionUpdate: function(nclicks, nclicks2, nclicks3, nclicks4, nclicks5, nclicks6, nclicks7, nclicks8,currentTime, duration) {
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

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'setup_pos_button.n_clicks') {
                const setup_pos = document.getElementById('setup_pos');
                const setup_index = setup_pos.innerText;
                if (nclicks4 > 0) {
                    return setup_index;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'minus_frame.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks5 > 0) {
                    const time = (currentTime - 1/fps)/duration
                    if (time < 0) {
                        return 0;
                    }
                    return time;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'plus_frame.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks6 > 0) {
                    const time = (currentTime + 1/fps)/duration
                    if (time > 1) {
                        return 0.999;
                    }
                    return time;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'minus_frame_mobile.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks7 > 0) {
                    const time = (currentTime - 1/fps)/duration
                    if (time < 0) {
                        return 0;
                    }
                    return time;
                }
            }

            else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'plus_frame_mobile.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks8 > 0) {
                    const time = (currentTime + 1/fps)/duration
                    if (time > 1) {
                        return 0.999;
                    }
                    return time;
                }
            }

            else {
                return currentTime;
            }

        },

        // Update the vertical line on the sequence plot
        drawVerticalLine: function(currentTime, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10) {

            // console.log(sequence.layout.shapes[0].x0)
            // console.log(fig1)

            function drawLine (fig, time, id) {
                fig.layout.shapes[0].x0 = time;
                fig.layout.shapes[0].x1 = time;
                Plotly.react(id , fig.data, fig.layout, {displayModeBar: false});
            }

            drawLine(fig1, currentTime, 'sequence');
            drawLine(fig2, currentTime, 'pelvis_rotation');
            drawLine(fig3, currentTime, 'pelvis_displacement');
            drawLine(fig4, currentTime, 'thorax_rotation');
            drawLine(fig5, currentTime, 'thorax_displacement');
            drawLine(fig6, currentTime, 's_tilt');
            drawLine(fig7, currentTime, 'h_tilt');
            drawLine(fig8, currentTime, 'h_rotation');
            drawLine(fig9, currentTime, 'arm_length');
            drawLine(fig10, currentTime, 'spine_rotation');

        }
    }
});
