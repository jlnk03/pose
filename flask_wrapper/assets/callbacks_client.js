window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // Update frame of video
        positionUpdate: function (nclicks, nclicks2, nclicks3, nclicks4, nclicks5, nclicks6, nclicks7, nclicks8, currentTime, duration) {

            // slider area
            const green_bar_pelvis_rot = document.getElementById('green_bar_pelvis_rot');
            const green_bar_pelvis_bend = document.getElementById('green_bar_pelvis_bend');
            const green_bar_thorax_rot = document.getElementById('green_bar_thorax_rot');
            const green_bar_thorax_bend = document.getElementById('green_bar_thorax_bend');
            const green_bar_head_rot = document.getElementById('green_bar_head_rot');
            const green_bar_head_tilt = document.getElementById('green_bar_head_tilt');
            const green_bar_pelvis_sway = document.getElementById('green_bar_pelvis_sway');
            const green_bar_thorax_sway = document.getElementById('green_bar_thorax_sway');

            // buttons
            let setup_pos_button = document.getElementById('setup_pos_button');
            let top_pos_button = document.getElementById('top_pos_button');
            let impact_pos_button = document.getElementById('impact_pos_button');
            let end_pos_button = document.getElementById('end_pos_button');

            // Settings
            let edit_positions = document.getElementById('edit_positions');
            const disabled = edit_positions.disabled;

            // console.log(window.dash_clientside.callback_context.triggered[0].prop_id)
            if (window.dash_clientside.callback_context.triggered[0].prop_id === 'top_pos_button.n_clicks') {
                top_pos_button.classList.replace('bg-transparent', 'bg-indigo-500');
                setup_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');
                impact_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');
                end_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');

                // text color white on pressed button
                top_pos_button.classList.replace('text-gray-400', 'text-white');
                setup_pos_button.classList.replace('text-white', 'text-gray-400');
                impact_pos_button.classList.replace('text-white', 'text-gray-400');
                end_pos_button.classList.replace('text-white', 'text-gray-400');

                // console.log(nclicks)
                const top_pos = document.getElementById('top_pos');
                const top_index = top_pos.innerText;

                const pelvis_rot_margins = document.getElementById('pelvis_rot_store').innerHTML.split(', ');
                const pelvis_bend_margins = document.getElementById('pelvis_bend_store').innerHTML.split(', ');
                const thorax_rot_margins = document.getElementById('thorax_rot_store').innerHTML.split(', ');
                const thorax_bend_margins = document.getElementById('thorax_bend_store').innerHTML.split(', ');
                const head_rot_margins = document.getElementById('head_rot_store').innerHTML.split(', ');
                const head_tilt_margins = document.getElementById('head_tilt_store').innerHTML.split(', ');
                const pelvis_sway_margins = document.getElementById('pelvis_sway_store').innerHTML.split(', ');
                const thorax_sway_margins = document.getElementById('thorax_sway_store').innerHTML.split(', ');

                edit_positions.classList.replace('bg-indigo-300', 'bg-indigo-500');
                edit_positions.classList.replace('dark:bg-indigo-800', 'dark:bg-indigo-500');
                edit_positions.classList.replace('dark:text-gray-400', 'dark:text-white');

                if (nclicks > 0) {
                    // green_bar_pelvis_rot.style.left = (80 + Number(pelvis_rot_margins[2])) / (240) * 100 + '%';
                    // green_bar_pelvis_rot.style.right = (160 - Number(pelvis_rot_margins[3])) / (240) * 100 + '%';
                    green_bar_pelvis_rot.style.background = newGradient(80, 160, pelvis_rot_margins[2], pelvis_rot_margins[3]);

                    // green_bar_pelvis_bend.style.left = (30 + Number(pelvis_bend_margins[2])) / (60) * 100 + '%';
                    // green_bar_pelvis_bend.style.right = (30 - Number(pelvis_bend_margins[3])) / (60) * 100 + '%';
                    green_bar_pelvis_bend.style.background = newGradient(30, 30, pelvis_bend_margins[2], pelvis_bend_margins[3]);

                    // green_bar_thorax_rot.style.left = (140 + Number(thorax_rot_margins[2])) / (280) * 100 + '%';
                    // green_bar_thorax_rot.style.right = (140 - Number(thorax_rot_margins[3])) / (280) * 100 + '%';
                    green_bar_thorax_rot.style.background = newGradient(140, 140, thorax_rot_margins[2], thorax_rot_margins[3]);

                    // green_bar_thorax_bend.style.left = (20 + Number(thorax_bend_margins[2])) / (80) * 100 + '%';
                    // green_bar_thorax_bend.style.right = (60 - Number(thorax_bend_margins[3])) / (80) * 100 + '%';
                    green_bar_thorax_bend.style.background = newGradient(20, 60, thorax_bend_margins[2], thorax_bend_margins[3]);

                    // green_bar_head_rot.style.left = (100 + Number(head_rot_margins[2])) / (200) * 100 + '%';
                    // green_bar_head_rot.style.right = (100 - Number(head_rot_margins[3])) / (200) * 100 + '%';
                    green_bar_head_rot.style.background = newGradient(100, 100, head_rot_margins[2], head_rot_margins[3]);

                    // green_bar_head_tilt.style.left = (60 + Number(head_tilt_margins[2])) / (120) * 100 + '%';
                    // green_bar_head_tilt.style.right = (60 - Number(head_tilt_margins[3])) / (120) * 100 + '%';
                    green_bar_head_tilt.style.background = newGradient(60, 60, head_tilt_margins[2], head_tilt_margins[3]);

                    // green_bar_pelvis_sway.style.left = (20 + Number(pelvis_sway_margins[2])) / (80) * 100 + '%';
                    // green_bar_pelvis_sway.style.right = (60 - Number(pelvis_sway_margins[3])) / (80) * 100 + '%';
                    green_bar_pelvis_sway.style.background = newGradient(20, 60, pelvis_sway_margins[2], pelvis_sway_margins[3]);

                    // green_bar_thorax_sway.style.left = (20 + Number(thorax_sway_margins[2])) / (80) * 100 + '%';
                    // green_bar_thorax_sway.style.right = (60 - Number(thorax_sway_margins[3])) / (80) * 100 + '%';
                    green_bar_thorax_sway.style.background = newGradient(20, 60, thorax_sway_margins[2], thorax_sway_margins[3]);

                    // Video index and enable edit button
                    return [top_index, false]
                }
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'impact_pos_button.n_clicks') {
                impact_pos_button.classList.replace('bg-transparent', 'bg-indigo-500');
                setup_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');
                top_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');
                end_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');

                // text color white on pressed button
                impact_pos_button.classList.replace('text-gray-400', 'text-white');
                setup_pos_button.classList.replace('text-white', 'text-gray-400');
                top_pos_button.classList.replace('text-white', 'text-gray-400');
                end_pos_button.classList.replace('text-white', 'text-gray-400');

                // console.log(nclicks2)
                const impact_pos = document.getElementById('impact_pos');
                const impact_index = impact_pos.innerText;

                const pelvis_rot_margins = document.getElementById('pelvis_rot_store').innerHTML.split(', ');
                const pelvis_bend_margins = document.getElementById('pelvis_bend_store').innerHTML.split(', ');
                const thorax_rot_margins = document.getElementById('thorax_rot_store').innerHTML.split(', ');
                const thorax_bend_margins = document.getElementById('thorax_bend_store').innerHTML.split(', ');
                const head_rot_margins = document.getElementById('head_rot_store').innerHTML.split(', ');
                const head_tilt_margins = document.getElementById('head_tilt_store').innerHTML.split(', ');
                const pelvis_sway_margins = document.getElementById('pelvis_sway_store').innerHTML.split(', ');
                const thorax_sway_margins = document.getElementById('thorax_sway_store').innerHTML.split(', ');

                edit_positions.classList.replace('bg-indigo-300', 'bg-indigo-500');
                edit_positions.classList.replace('dark:bg-indigo-800', 'dark:bg-indigo-500');
                edit_positions.classList.replace('dark:text-gray-400', 'dark:text-white');

                if (nclicks2 > 0) {
                    // green_bar_pelvis_rot.style.left = (80 + Number(pelvis_rot_margins[4])) / (240) * 100 + '%';
                    // green_bar_pelvis_rot.style.right = (160 - Number(pelvis_rot_margins[5])) / (240) * 100 + '%';
                    green_bar_pelvis_rot.style.background = newGradient(80, 160, pelvis_rot_margins[4], pelvis_rot_margins[5]);

                    // green_bar_pelvis_bend.style.left = (30 + Number(pelvis_bend_margins[4])) / (60) * 100 + '%';
                    // green_bar_pelvis_bend.style.right = (30 - Number(pelvis_bend_margins[5])) / (60) * 100 + '%';
                    green_bar_pelvis_bend.style.background = newGradient(30, 30, pelvis_bend_margins[4], pelvis_bend_margins[5]);

                    // green_bar_thorax_rot.style.left = (140 + Number(thorax_rot_margins[4])) / (280) * 100 + '%';
                    // green_bar_thorax_rot.style.right = (140 - Number(thorax_rot_margins[5])) / (280) * 100 + '%';
                    green_bar_thorax_rot.style.background = newGradient(140, 140, thorax_rot_margins[4], thorax_rot_margins[5]);

                    // green_bar_thorax_bend.style.left = (20 + Number(thorax_bend_margins[4])) / (80) * 100 + '%';
                    // green_bar_thorax_bend.style.right = (60 - Number(thorax_bend_margins[5])) / (80) * 100 + '%';
                    green_bar_thorax_bend.style.background = newGradient(20, 60, thorax_bend_margins[4], thorax_bend_margins[5]);

                    // green_bar_head_rot.style.left = (100 + Number(head_rot_margins[4])) / (200) * 100 + '%';
                    // green_bar_head_rot.style.right = (100 - Number(head_rot_margins[5])) / (200) * 100 + '%';
                    green_bar_head_rot.style.background = newGradient(100, 100, head_rot_margins[4], head_rot_margins[5]);

                    // green_bar_head_tilt.style.left = (60 + Number(head_tilt_margins[4])) / (120) * 100 + '%';
                    // green_bar_head_tilt.style.right = (60 - Number(head_tilt_margins[5])) / (120) * 100 + '%';
                    green_bar_head_tilt.style.background = newGradient(60, 60, head_tilt_margins[4], head_tilt_margins[5]);

                    // green_bar_pelvis_sway.style.left = (20 + Number(pelvis_sway_margins[4])) / (80) * 100 + '%';
                    // green_bar_pelvis_sway.style.right = (60 - Number(pelvis_sway_margins[5])) / (80) * 100 + '%';
                    green_bar_pelvis_sway.style.background = newGradient(20, 60, pelvis_sway_margins[4], pelvis_sway_margins[5]);

                    // green_bar_thorax_sway.style.left = (20 + Number(thorax_sway_margins[4])) / (80) * 100 + '%';
                    // green_bar_thorax_sway.style.right = (60 - Number(thorax_sway_margins[5])) / (80) * 100 + '%';
                    green_bar_thorax_sway.style.background = newGradient(20, 60, thorax_sway_margins[4], thorax_sway_margins[5]);

                    return [impact_index, false]
                }
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'end_pos_button.n_clicks') {
                end_pos_button.classList.replace('bg-transparent', 'bg-indigo-500');
                setup_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');
                top_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');
                impact_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');

                // text color white on pressed button
                end_pos_button.classList.replace('text-gray-400', 'text-white');
                setup_pos_button.classList.replace('text-white', 'text-gray-400');
                top_pos_button.classList.replace('text-white', 'text-gray-400');
                impact_pos_button.classList.replace('text-white', 'text-gray-400');

                const end_pos = document.getElementById('end_pos');
                const end_index = end_pos.innerText;

                edit_positions.classList.replace('bg-indigo-300', 'bg-indigo-500');
                edit_positions.classList.replace('dark:bg-indigo-800', 'dark:bg-indigo-500');
                edit_positions.classList.replace('dark:text-gray-400', 'dark:text-white');

                if (nclicks3 > 0) {

                    green_bar_pelvis_rot.style.background = resetGradient()
                    green_bar_pelvis_bend.style.background = resetGradient()
                    green_bar_thorax_rot.style.background = resetGradient()
                    green_bar_thorax_bend.style.background = resetGradient()
                    green_bar_head_rot.style.background = resetGradient()
                    green_bar_head_tilt.style.background = resetGradient()
                    green_bar_pelvis_sway.style.background = resetGradient()
                    green_bar_thorax_sway.style.background = resetGradient()

                    return [end_index, false]
                }
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'setup_pos_button.n_clicks') {
                setup_pos_button.classList.replace('bg-transparent', 'bg-indigo-500');
                top_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');
                impact_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');
                end_pos_button.classList.replace('bg-indigo-500', 'bg-transparent');

                // text color to white on pressed button
                setup_pos_button.classList.replace('text-gray-400', 'text-white');
                top_pos_button.classList.replace('text-white', 'text-gray-400');
                impact_pos_button.classList.replace('text-white', 'text-gray-400');
                end_pos_button.classList.replace('text-white', 'text-gray-400');

                const setup_pos = document.getElementById('setup_pos');
                const setup_index = setup_pos.innerText;

                const pelvis_rot_margins = document.getElementById('pelvis_rot_store').innerHTML.split(', ');
                const pelvis_bend_margins = document.getElementById('pelvis_bend_store').innerHTML.split(', ');
                const thorax_rot_margins = document.getElementById('thorax_rot_store').innerHTML.split(', ');
                const thorax_bend_margins = document.getElementById('thorax_bend_store').innerHTML.split(', ');
                const head_rot_margins = document.getElementById('head_rot_store').innerHTML.split(', ');
                const head_tilt_margins = document.getElementById('head_tilt_store').innerHTML.split(', ');
                const pelvis_sway_margins = document.getElementById('pelvis_sway_store').innerHTML.split(', ');
                const thorax_sway_margins = document.getElementById('thorax_sway_store').innerHTML.split(', ');

                edit_positions.classList.replace('bg-indigo-300', 'bg-indigo-500');
                edit_positions.classList.replace('dark:bg-indigo-800', 'dark:bg-indigo-500');
                edit_positions.classList.replace('dark:text-gray-400', 'dark:text-white');

                // console.log(pelvis_rot_margins)

                if (nclicks4 > 0) {
                    // green_bar_pelvis_rot.style.left = (80 + Number(pelvis_rot_margins[0])) / (240) * 100 + '%';
                    // green_bar_pelvis_rot.style.right = (160 - Number(pelvis_rot_margins[1])) / (240) * 100 + '%';
                    green_bar_pelvis_rot.style.background = newGradient(80, 160, pelvis_rot_margins[0], pelvis_rot_margins[1]);

                    // green_bar_pelvis_bend.style.left = (30 + Number(pelvis_bend_margins[0])) / (60) * 100 + '%';
                    // green_bar_pelvis_bend.style.right = (30 - Number(pelvis_bend_margins[1])) / (60) * 100 + '%';
                    green_bar_pelvis_bend.style.background = newGradient(30, 30, pelvis_bend_margins[0], pelvis_bend_margins[1]);

                    // green_bar_thorax_rot.style.left = (140 + Number(thorax_rot_margins[0])) / (280) * 100 + '%';
                    // green_bar_thorax_rot.style.right = (140 - Number(thorax_rot_margins[1])) / (280) * 100 + '%';
                    green_bar_thorax_rot.style.background = newGradient(140, 140, thorax_rot_margins[0], thorax_rot_margins[1]);

                    // green_bar_thorax_bend.style.left = (20 + Number(thorax_bend_margins[0])) / (80) * 100 + '%';
                    // green_bar_thorax_bend.style.right = (60 - Number(thorax_bend_margins[1])) / (80) * 100 + '%';
                    green_bar_thorax_bend.style.background = newGradient(20, 60, thorax_bend_margins[0], thorax_bend_margins[1]);

                    // green_bar_head_rot.style.left = (100 + Number(head_rot_margins[0])) / (200) * 100 + '%';
                    // green_bar_head_rot.style.right = (100 - Number(head_rot_margins[1])) / (200) * 100 + '%';
                    green_bar_head_rot.style.background = newGradient(100, 100, head_rot_margins[0], head_rot_margins[1]);

                    // green_bar_head_tilt.style.left = (60 + Number(head_tilt_margins[0])) / (120) * 100 + '%';
                    // green_bar_head_tilt.style.right = (60 - Number(head_tilt_margins[1])) / (120) * 100 + '%';
                    green_bar_head_tilt.style.background = newGradient(60, 60, head_tilt_margins[0], head_tilt_margins[1]);

                    // green_bar_pelvis_sway.style.left = (20 + Number(pelvis_sway_margins[0])) / (80) * 100 + '%';
                    // green_bar_pelvis_sway.style.right = (60 - Number(pelvis_sway_margins[1])) / (80) * 100 + '%';
                    green_bar_pelvis_sway.style.background = newGradient(20, 60, pelvis_sway_margins[0], pelvis_sway_margins[1]);

                    // green_bar_thorax_sway.style.left = (20 + Number(thorax_sway_margins[0])) / (80) * 100 + '%';
                    // green_bar_thorax_sway.style.right = (60 - Number(thorax_sway_margins[1])) / (80) * 100 + '%';
                    green_bar_thorax_sway.style.background = newGradient(20, 60, thorax_sway_margins[0], thorax_sway_margins[1]);

                    return [setup_index, false]
                }
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'minus_frame.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks5 > 0) {
                    const time = (currentTime - 1 / fps) / duration
                    if (time < 0) {
                        return [0, disabled];
                    }
                    return [time, disabled];
                }
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'plus_frame.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks6 > 0) {
                    const time = (currentTime + 1 / fps) / duration
                    if (time > 1) {
                        return [0.999, disabled];
                    }
                    return [time, disabled];
                }
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'minus_frame_mobile.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks7 > 0) {
                    const time = (currentTime - 1 / fps) / duration
                    if (time < 0) {
                        return [0, disabled];
                    }
                    return [time, disabled];
                }
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'plus_frame_mobile.n_clicks') {
                const fps_saved = document.getElementById('fps_saved');
                const fps = fps_saved.innerText;
                if (nclicks8 > 0) {
                    const time = (currentTime + 1 / fps) / duration
                    if (time > 1) {
                        return [0.999, disabled];
                    }
                    return [time, disabled];
                }
            } else {
                return [currentTime, disabled];
            }

        },

        // Update the vertical line on the sequence plot
        drawVerticalLine: function (currentTime, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10) {

            // console.log(sequence.layout.shapes[0].x0)
            // console.log(fig1)

            function drawLine(fig, time, id) {
                fig.layout.shapes[0].x0 = time;
                fig.layout.shapes[0].x1 = time;
                Plotly.react(id, fig.data, fig.layout, {displayModeBar: false});
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

        },

        // Update the values of the sliders
        updateValues: function (currentTime, duration, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, impact_button_time, top_button_time, end_button_time, setup_button_time) {
            // console.log('updateValues')
            const pelvis_rotation = fig2.data[1].y;
            const pelvis_bend = fig2.data[0].y;
            const thorax_rotation = fig4.data[0].y;
            const thorax_bend = fig4.data[1].y;
            const head_tilt = fig7.data[0].y;
            const head_rotation = fig8.data[0].y;
            const arm_rotation = fig11.data[0].y;
            const arm_ground = fig11.data[1].y;
            const pelvis_sway = fig3.data[1].y;
            const thorax_sway = fig5.data[1].y;

            let index = Math.floor(pelvis_rotation.length * (currentTime / duration))

            if (index >= pelvis_rotation.length) {
                index = pelvis_rotation.length - 1;
            }

            const value_pelvis_rotation = Math.round(pelvis_rotation[index]);
            const value_pelvis_bend = Math.round(pelvis_bend[index]);
            const value_thorax_rotation = Math.round(thorax_rotation[index]);
            const value_thorax_bend = Math.round(thorax_bend[index]);
            const value_head_tilt = Math.round(head_tilt[index]);
            const value_head_rotation = Math.round(head_rotation[index]);
            const value_arm_rotation = Math.round(arm_rotation[index]);
            const value_arm_ground = Math.round(arm_ground[index]);
            const value_pelvis_sway = Math.round(pelvis_sway[index] * 100);
            const value_thorax_sway = Math.round(thorax_sway[index] * 100);

            // Color the values
            const pelvis_rot_div = document.getElementById('pelvis_rot_val');
            const pelvis_bend_div = document.getElementById('pelvis_bend_val');
            const thorax_rot_div = document.getElementById('thorax_rot_val');
            const thorax_bend_div = document.getElementById('thorax_bend_val');
            const head_rot_div = document.getElementById('head_rot_val');
            const head_tilt_div = document.getElementById('head_tilt_val');
            // const arm_rot_div = document.getElementById('arm_rot_val');
            // const arm_ground_div = document.getElementById('arm_ground_val');
            const pelvis_sway_div = document.getElementById('pelvis_sway_val');
            const thorax_sway_div = document.getElementById('thorax_sway_val');

            // Sliders
            const slider_pelvis_rot = document.getElementById('slider_pelvis_rot');
            const slider_pelvis_bend = document.getElementById('slider_pelvis_bend');
            const slider_thorax_rot = document.getElementById('slider_thorax_rot');
            const slider_thorax_bend = document.getElementById('slider_thorax_bend');
            const slider_head_rot = document.getElementById('slider_head_rot');
            const slider_head_tilt = document.getElementById('slider_head_tilt');
            const slider_arm_rot = document.getElementById('slider_arm_rot');
            const slider_arm_ground = document.getElementById('slider_arm_ground');
            const slider_pelvis_sway = document.getElementById('slider_pelvis_sway');
            const slider_thorax_sway = document.getElementById('slider_thorax_sway');

            // Margins
            const margin_pelvis_rot = document.getElementById('pelvis_rot_store').innerHTML.split(', ')
            const margin_pelvis_bend = document.getElementById('pelvis_bend_store').innerHTML.split(', ')
            const margin_thorax_rot = document.getElementById('thorax_rot_store').innerHTML.split(', ')
            const margin_thorax_bend = document.getElementById('thorax_bend_store').innerHTML.split(', ')
            const margin_head_rot = document.getElementById('head_rot_store').innerHTML.split(', ')
            const margin_head_tilt = document.getElementById('head_tilt_store').innerHTML.split(', ')
            // const margin_arm_rot = document.getElementById('arm_rot_store').innerHTML.split(', ')
            // const margin_arm_ground = document.getElementById('arm_ground_store').innerHTML.split(', ')
            const margin_pelvis_sway = document.getElementById('pelvis_sway_store').innerHTML.split(', ')
            const margin_thorax_sway = document.getElementById('thorax_sway_store').innerHTML.split(', ')

            // Gradient bars
            const green_bar_pelvis_rot = document.getElementById('green_bar_pelvis_rot');
            const green_bar_pelvis_bend = document.getElementById('green_bar_pelvis_bend');
            const green_bar_thorax_rot = document.getElementById('green_bar_thorax_rot');
            const green_bar_thorax_bend = document.getElementById('green_bar_thorax_bend');
            const green_bar_head_rot = document.getElementById('green_bar_head_rot');
            const green_bar_head_tilt = document.getElementById('green_bar_head_tilt');
            const green_bar_pelvis_sway = document.getElementById('green_bar_pelvis_sway');
            const green_bar_thorax_sway = document.getElementById('green_bar_thorax_sway');

            if (impact_button_time === undefined) {
                impact_button_time = -1
            }
            if (top_button_time === undefined) {
                top_button_time = -1
            }
            if (end_button_time === undefined) {
                end_button_time = -1
            }
            if (setup_button_time === undefined) {
                setup_button_time = -1
            }

            const button_recent = {
                'impact': impact_button_time,
                'top': top_button_time,
                'end': end_button_time,
                'setup': setup_button_time,
                'default': 0
            }
            // sort button_recent by value
            const button_recent_sorted = Object.keys(button_recent).sort(function (a, b) {
                return button_recent[a] - button_recent[b]
            })
            // get the most recent button
            const button_recent_name = button_recent_sorted[button_recent_sorted.length - 1]

            // TODO: make this a function

            if (button_recent_name === 'impact') {
                pelvis_rot_div.style.color = getColorFromGradient(green_bar_pelvis_rot, -80, 160, value_pelvis_rotation);
                pelvis_bend_div.style.color = getColorFromGradient(green_bar_pelvis_bend, -30, 30, value_pelvis_bend);
                thorax_rot_div.style.color = getColorFromGradient(green_bar_thorax_rot, -140, 140, value_thorax_rotation);
                thorax_bend_div.style.color = getColorFromGradient(green_bar_thorax_bend, -20, 60, value_thorax_bend);
                head_rot_div.style.color = getColorFromGradient(green_bar_head_rot, -100, 100, value_head_rotation);
                head_tilt_div.style.color = getColorFromGradient(green_bar_head_tilt, -60, 60, value_head_tilt);
                // pelvis_sway_div.style.color = getColorFromGradient(green_bar_pelvis_sway, -20, 60, value_pelvis_sway);
                // thorax_sway_div.style.color = getColorFromGradient(green_bar_thorax_sway, -20, 60, value_thorax_sway);
                // pelvis_rot_div.style.color = ((value_pelvis_rotation < margin_pelvis_rot[4]) || (value_pelvis_rotation > margin_pelvis_rot[5])) ? 'red' : 'green';
                // pelvis_bend_div.style.color = ((value_pelvis_bend < margin_pelvis_bend[4]) || (value_pelvis_bend > margin_pelvis_bend[5])) ? 'red' : 'green';
                // thorax_rot_div.style.color = ((value_thorax_rotation < margin_thorax_rot[4]) || (value_thorax_rotation > margin_thorax_rot[5])) ? 'red' : 'green';
                // thorax_bend_div.style.color = ((value_thorax_bend < margin_thorax_bend[4]) || (value_thorax_bend > margin_thorax_bend[5])) ? 'red' : 'green';
                // head_rot_div.style.color = ((value_head_rotation < margin_head_rot[4]) || (value_head_rotation > margin_head_rot[5])) ? 'red' : 'green';
                // head_tilt_div.style.color = ((value_head_tilt < margin_head_tilt[4]) || (value_head_tilt > margin_head_tilt[5])) ? 'red' : 'green';
                // pelvis_sway_div.style.color = ((value_pelvis_sway < margin_pelvis_sway[4]) || (value_pelvis_sway > margin_pelvis_sway[5])) ? 'red' : 'green';
                // thorax_sway_div.style.color = ((value_thorax_sway < margin_thorax_sway[4]) || (value_thorax_sway > margin_thorax_sway[5])) ? 'red' : 'green';

            } else if (button_recent_name === 'top') {
                pelvis_rot_div.style.color = getColorFromGradient(green_bar_pelvis_rot, -80, 160, value_pelvis_rotation);
                pelvis_bend_div.style.color = getColorFromGradient(green_bar_pelvis_bend, -30, 30, value_pelvis_bend);
                thorax_rot_div.style.color = getColorFromGradient(green_bar_thorax_rot, -140, 140, value_thorax_rotation);
                thorax_bend_div.style.color = getColorFromGradient(green_bar_thorax_bend, -20, 60, value_thorax_bend);
                head_rot_div.style.color = getColorFromGradient(green_bar_head_rot, -100, 100, value_head_rotation);
                head_tilt_div.style.color = getColorFromGradient(green_bar_head_tilt, -60, 60, value_head_tilt);
                // pelvis_rot_div.style.color = ((value_pelvis_rotation < margin_pelvis_rot[2]) || (value_pelvis_rotation > margin_pelvis_rot[3])) ? 'red' : 'green';
                // pelvis_bend_div.style.color = ((value_pelvis_bend < margin_pelvis_bend[2]) || (value_pelvis_bend > margin_pelvis_bend[3])) ? 'red' : 'green';
                // thorax_rot_div.style.color = ((value_thorax_rotation < margin_thorax_rot[2]) || (value_thorax_rotation > margin_thorax_rot[3])) ? 'red' : 'green';
                // thorax_bend_div.style.color = ((value_thorax_bend < margin_thorax_bend[2]) || (value_thorax_bend > margin_thorax_bend[3])) ? 'red' : 'green';
                // head_rot_div.style.color = ((value_head_rotation < margin_head_rot[2]) || (value_head_rotation > margin_head_rot[3])) ? 'red' : 'green';
                // head_tilt_div.style.color = ((value_head_tilt < margin_head_tilt[2]) || (value_head_tilt > margin_head_tilt[3])) ? 'red' : 'green';
                // pelvis_sway_div.style.color = ((value_pelvis_sway < margin_pelvis_sway[2]) || (value_pelvis_sway > margin_pelvis_sway[3])) ? 'red' : 'green';
                // thorax_sway_div.style.color = ((value_thorax_sway < margin_thorax_sway[2]) || (value_thorax_sway > margin_thorax_sway[3])) ? 'red' : 'green';

            } else if (button_recent_name === 'setup') {
                pelvis_rot_div.style.color = getColorFromGradient(green_bar_pelvis_rot, -80, 160, value_pelvis_rotation);
                pelvis_bend_div.style.color = getColorFromGradient(green_bar_pelvis_bend, -30, 30, value_pelvis_bend);
                thorax_rot_div.style.color = getColorFromGradient(green_bar_thorax_rot, -140, 140, value_thorax_rotation);
                thorax_bend_div.style.color = getColorFromGradient(green_bar_thorax_bend, -20, 60, value_thorax_bend);
                head_rot_div.style.color = getColorFromGradient(green_bar_head_rot, -100, 100, value_head_rotation);
                head_tilt_div.style.color = getColorFromGradient(green_bar_head_tilt, -60, 60, value_head_tilt);
                // pelvis_rot_div.style.color = ((value_pelvis_rotation < margin_pelvis_rot[0]) || (value_pelvis_rotation > margin_pelvis_rot[1])) ? 'red' : 'green';
                // pelvis_bend_div.style.color = ((value_pelvis_bend < margin_pelvis_bend[0]) || (value_pelvis_bend > margin_pelvis_bend[1])) ? 'red' : 'green';
                // thorax_rot_div.style.color = ((value_thorax_rotation < margin_thorax_rot[0]) || (value_thorax_rotation > margin_thorax_rot[1])) ? 'red' : 'green';
                // thorax_bend_div.style.color = ((value_thorax_bend < margin_thorax_bend[0]) || (value_thorax_bend > margin_thorax_bend[1])) ? 'red' : 'green';
                // head_rot_div.style.color = ((value_head_rotation < margin_head_rot[0]) || (value_head_rotation > margin_head_rot[1])) ? 'red' : 'green';
                // head_tilt_div.style.color = ((value_head_tilt < margin_head_tilt[0]) || (value_head_tilt > margin_head_tilt[1])) ? 'red' : 'green';
                // pelvis_sway_div.style.color = ((value_pelvis_sway < margin_pelvis_sway[0]) || (value_pelvis_sway > margin_pelvis_sway[1])) ? 'red' : 'green';
                // thorax_sway_div.style.color = ((value_thorax_sway < margin_thorax_sway[0]) || (value_thorax_sway > margin_thorax_sway[1])) ? 'red' : 'green';

            } else {
                pelvis_rot_div.style.color = '';
                pelvis_bend_div.style.color = '';
                thorax_rot_div.style.color = '';
                thorax_bend_div.style.color = '';
                head_rot_div.style.color = '';
                head_tilt_div.style.color = '';
                pelvis_sway_div.style.color = '';
                thorax_sway_div.style.color = '';
            }

            if (isNaN(value_pelvis_rotation)) {
                return ['-°', '-°', '-°', '-°', '-°', '-°', '-°', '-°'];
            }

            // Move sliders
            slider_pelvis_rot.style.left = (value_pelvis_rotation + 80) / (240) * 100 + '%';
            slider_pelvis_bend.style.left = (value_pelvis_bend + 40) / (80) * 100 + '%';
            slider_thorax_rot.style.left = (value_thorax_rotation + 140) / (280) * 100 + '%';
            slider_thorax_bend.style.left = (value_thorax_bend + 20) / (80) * 100 + '%';
            slider_head_rot.style.left = (value_head_rotation + 100) / (200) * 100 + '%';
            slider_head_tilt.style.left = (value_head_tilt + 60) / (120) * 100 + '%';
            slider_arm_rot.style.left = (value_arm_rotation + 240) / (480) * 100 + '%';
            slider_arm_ground.style.left = (value_arm_ground + 90) / (180) * 100 + '%';
            slider_pelvis_sway.style.left = (value_pelvis_sway + 40) / (80) * 100 + '%';
            slider_thorax_sway.style.left = (value_thorax_sway + 40) / (80) * 100 + '%';

            return [`${value_pelvis_rotation}°`, `${value_pelvis_bend}°`, `${value_thorax_rotation}°`, `${value_thorax_bend}°`,
                `${value_head_rotation}°`, `${value_head_tilt}°`, `${value_arm_rotation}°`, `${value_arm_ground}°`, `${value_pelvis_sway}cm`, `${value_thorax_sway}cm`];
        },

        showNavbar: function (n_clicks, header_clicks, mobile_clicks, sidebar_class, navbar_main_class) {
            if (window.dash_clientside.callback_context.triggered[0].prop_id === 'menu-button.n_clicks') {
                sidebar_class = sidebar_class.replace('hidden', 'flex')
                navbar_main_class = navbar_main_class.replace('hidden', 'lg:hidden')

                return [sidebar_class, navbar_main_class]
            }

            sidebar_class = sidebar_class.replace('flex', 'hidden')
            navbar_main_class = navbar_main_class.replace('lg:hidden', 'hidden')

            return [sidebar_class, navbar_main_class]

        },

        hideSelectionView: function (n_clicks) {

            let pelvis_rot_store = document.getElementById('pelvis_rot_store')
            let pelvis_tilt_store = document.getElementById('pelvis_bend_store')
            let thorax_rot_store = document.getElementById('thorax_rot_store')
            let thorax_tilt_store = document.getElementById('thorax_bend_store')
            let head_rot_store = document.getElementById('head_rot_store')
            let head_tilt_store = document.getElementById('head_tilt_store')

            const setup_low = document.getElementById('setup_low_new_margins').value
            const setup_high = document.getElementById('setup_high_new_margins').value
            const top_low = document.getElementById('top_low_new_margins').value
            const top_high = document.getElementById('top_high_new_margins').value
            const impact_low = document.getElementById('impact_low_new_margins').value
            const impact_high = document.getElementById('impact_high_new_margins').value

            const body_part = document.getElementById('new_margins_title').innerHTML
            // console.log(body_part)

            if (body_part.includes('Pelvis Rot')) {
                pelvis_rot_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            } else if (body_part.includes('Pelvis Tilt')) {
                pelvis_tilt_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            } else if (body_part.includes('Thorax Rot')) {
                thorax_rot_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            } else if (body_part.includes('Thorax Tilt')) {
                thorax_tilt_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            } else if (body_part.includes('Head Rot')) {
                head_rot_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            } else if (body_part.includes('Head Tilt')) {
                head_tilt_store.innerHTML = setup_low + ', ' + setup_high + ', ' + top_low + ', ' + top_high + ', ' + impact_low + ', ' + impact_high
            } else {
                console.log('No body part selected')
            }

            let selection_view_dismiss = document.getElementById('selection-view-dismiss').classList
            selection_view_dismiss.toggle('hidden')

            let selection_class = document.getElementById('selection-view').classList
            selection_class.toggle('hidden')

            // return selection_class.replace('flex', 'hidden');

        },

        showSelectionView: function (n_clicks, n_clicks2, n_clicks3, n_clicks4, n_clicks5, n_clicks6) {

            const title = document.getElementById('new_margins_title');
            let selection_view_dismiss = document.getElementById('selection-view-dismiss').classList
            selection_view_dismiss.toggle('hidden')

            let selection_class = document.getElementById('selection-view').classList
            selection_class.toggle('hidden')

            // let setup_low = document.getElementById('setup_low_new_margins')
            // let setup_high = document.getElementById('setup_high_new_margins')
            // let top_low = document.getElementById('top_low_new_margins')
            // let top_high = document.getElementById('top_high_new_margins')
            // let impact_low = document.getElementById('impact_low_new_margins')
            // let impact_high = document.getElementById('impact_high_new_margins')
            let setup_low = 0
            let setup_high = 0
            let top_low = 0
            let top_high = 0
            let impact_low = 0
            let impact_high = 0

            if (window.dash_clientside.callback_context.triggered[0].prop_id === 'pelvis_rot_btn.n_clicks') {
                const pelvis_rot_store = document.getElementById('pelvis_rot_store').innerHTML
                // console.log(pelvis_rot_store)
                const pelvis_rot = pelvis_rot_store.split(', ')

                // Default values for input fields
                setup_low = pelvis_rot[0]
                setup_high = pelvis_rot[1]
                top_low = pelvis_rot[2]
                top_high = pelvis_rot[3]
                impact_low = pelvis_rot[4]
                impact_high = pelvis_rot[5]

                title.innerHTML = 'New Margins for Pelvis Rotation';
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'pelvis_tilt_btn.n_clicks') {
                const pelvis_tilt_store = document.getElementById('pelvis_bend_store').innerHTML
                const pelvis_tilt = pelvis_tilt_store.split(', ')

                setup_low = pelvis_tilt[0]
                setup_high = pelvis_tilt[1]
                top_low = pelvis_tilt[2]
                top_high = pelvis_tilt[3]
                impact_low = pelvis_tilt[4]
                impact_high = pelvis_tilt[5]

                title.innerHTML = 'New Margins for Pelvis Tilt';
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'thorax_rot_btn.n_clicks') {
                const thorax_rot_store = document.getElementById('thorax_rot_store').innerHTML
                const thorax_rot = thorax_rot_store.split(', ')

                setup_low = thorax_rot[0]
                setup_high = thorax_rot[1]
                top_low = thorax_rot[2]
                top_high = thorax_rot[3]
                impact_low = thorax_rot[4]
                impact_high = thorax_rot[5]

                title.innerHTML = 'New Margins for Thorax Rotation';
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'thorax_tilt_btn.n_clicks') {
                const thorax_tilt_store = document.getElementById('thorax_bend_store').innerHTML
                const thorax_tilt = thorax_tilt_store.split(', ')

                setup_low = thorax_tilt[0]
                setup_high = thorax_tilt[1]
                top_low = thorax_tilt[2]
                top_high = thorax_tilt[3]
                impact_low = thorax_tilt[4]
                impact_high = thorax_tilt[5]

                title.innerHTML = 'New Margins for Thorax Bend';
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'head_rot_btn.n_clicks') {
                const head_rot_store = document.getElementById('head_rot_store').innerHTML
                const head_rot = head_rot_store.split(', ')

                setup_low = head_rot[0]
                setup_high = head_rot[1]
                top_low = head_rot[2]
                top_high = head_rot[3]
                impact_low = head_rot[4]
                impact_high = head_rot[5]

                title.innerHTML = 'New Margins for Head Rotation';
            } else if (window.dash_clientside.callback_context.triggered[0].prop_id === 'head_tilt_btn.n_clicks') {
                const head_tilt_store = document.getElementById('head_tilt_store').innerHTML
                const head_tilt = head_tilt_store.split(', ')

                setup_low = head_tilt[0]
                setup_high = head_tilt[1]
                top_low = head_tilt[2]
                top_high = head_tilt[3]
                impact_low = head_tilt[4]
                impact_high = head_tilt[5]

                title.innerHTML = 'New Margins for Head Tilt';
            } else {
                title.innerHTML = 'New Margins';
            }

            return [setup_low, setup_high, top_low, top_high, impact_low, impact_high];

        },

        hideSelectionViewCross: function (n_clicks) {
            let selection_class = document.getElementById('selection-view').classList
            selection_class.toggle('hidden')
            let selection_view_dismiss = document.getElementById('selection-view-dismiss').classList
            selection_view_dismiss.toggle('hidden')
        },

        tempoSlider: function (tempo) {
            const gradient = document.getElementById('tempo_slider_gradient');
            const positionPercent = tempo / 6; // get the color at 50% position
            const computedStyle = getComputedStyle(gradient);
            const regex = /rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)/g;
            const rgbColors = computedStyle.backgroundImage.match(regex);
            // const gradientColors = computedStyle.backgroundImage.split(', ');
            // console.log(rgbColors)

            let maxColorIndex = Math.ceil((rgbColors.length - 1) * positionPercent)
            if (maxColorIndex > rgbColors.length - 1) {
                maxColorIndex = rgbColors.length - 1
            }

            if (maxColorIndex === 0) {
                maxColorIndex = 1
            }

            const minColorIndex = maxColorIndex - 1

            const maxColor = rgbColors[maxColorIndex]
            const minColor = rgbColors[minColorIndex]

            let percent = (positionPercent - (minColorIndex / (rgbColors.length - 1))) / (1 / (rgbColors.length - 1))

            if (positionPercent < 0) {
                percent = 0
            }
            if (positionPercent > 1) {
                percent = 1
            }

            const resultColor = blendColors(minColor, maxColor, percent);

            let tempo_div = document.getElementById('tempo_div')
            tempo_div.style.color = resultColor

            function blendColors(color1, color2, percent) {
                // console.log(color1, color2, percent)
                const [r1, g1, b1] = color1.match(/\d+/g).map(Number);
                const [r2, g2, b2] = color2.match(/\d+/g).map(Number);
                const r = Math.round(r1 + (r2 - r1) * percent);
                const g = Math.round(g1 + (g2 - g1) * percent);
                const b = Math.round(b1 + (b2 - b1) * percent);
                return `rgb(${r}, ${g}, ${b})`;
            }

            return {'left': tempo / 6 * 100 + '%'}
        },

        backswingSlider: function (backswing) {
            backswing = Number(backswing.split(' ')[0])
            return {'left': backswing / 1.5 * 100 + '%'}
        },

        downswingSlider: function (downswing) {
            downswing = Number(downswing.split(' ')[0])
            return {'left': downswing / 0.5 * 100 + '%'}
        },

        toggleHeart: function (n_clicks, url) {
            if (n_clicks > 0) {
                let file = url.split('/')[3];
                let heart = document.getElementById('heart');
                let heart_navbar = document.getElementById(`heart_${file}`);
                heart.classList.toggle('is-active');
                heart_navbar.classList.toggle('is-active');
            }
        },

        toggleDeleteView: function (n_clicks) {
            if (n_clicks > 0) {
                // console.log(n_clicks)
                let delete_view = document.getElementById('delete-file-view').classList
                delete_view.toggle('hidden')

                return 0

            }
        },

        hideDeleteView: function (n_clicks, n_clicks2) {
            if ((n_clicks !== null) || (n_clicks2 !== null)) {
                let delete_view = document.getElementById('delete-file-view').classList
                delete_view.toggle('hidden')
            }
        },

        deleteViewFile: function (n_clicks) {
            if (n_clicks !== null) {
                let button = window.dash_clientside.callback_context.triggered[0].prop_id
                button = button.split('.')[0]
                button = JSON.parse(button)
                button = button['index']
                return button
            }
        },

        showEditPositionsSaveButton: function (n_clicks, n_clicks2, n_clicks3) {
            if (n_clicks > 0 || n_clicks2 > 0 || n_clicks3 > 0) {
                let button = document.getElementById('edit_positions_div').classList
                button.toggle('hidden')
            }
        },

        showOverlay: function (n_clicks, n_clicks2, n_clicks3) {
            // if (n_clicks > 0 || n_clicks2 > 0 || n_clicks3 > 0) {
            if (window.dash_clientside.callback_context.triggered[0].value > 0) {
                let overlay = document.getElementById('overlay').classList
                overlay.toggle('hidden')

                let main_wrapper = document.getElementById('main_wrapper').classList
                main_wrapper.toggle('overflow-hidden')

                let body = document.getElementById('body').classList
                body.toggle('overflow-hidden')

            }
        },

        showFigures: function (value) {
            let figureContainer = document.getElementById('figures-container').classList
            let liveDivs = document.getElementById('live-divs').classList
            let video = document.getElementById('video-view').classList
            let expertToggleBG = document.getElementById('expert-toggle-bg').classList
            let expertTogggleCircle = document.getElementById('expert-toggle-circle').classList
            figureContainer.toggle('hidden')
            liveDivs.toggle('hidden')
            expertToggleBG.toggle('bg-indigo-400')
            expertToggleBG.toggle('dark:bg-indigo-600')
            expertTogggleCircle.toggle('left-auto')
            video.toggle('mb-10')
        },

        // showVideoFrames: function (n_clicks, n_clicks2, setup, impact, top) {
        //     if (n_clicks === 1 || n_clicks2 === 1) {
        showVideoFrames: function (url, setup, impact, top) {
            if (url !== null) {
                var videoContainer = document.getElementById('video')
                var video = videoContainer.getElementsByTagName('video')[0]
                // check if video element is already present in the DOM otherwise wait for it to load
                if (videoContainer.childElementCount === 0) {
                    // check every 100ms if video is loaded
                    var checkExist = setInterval(function () {
                        if (videoContainer.childElementCount > 0) {
                            video = videoContainer.getElementsByTagName('video')[0]
                            clearInterval(checkExist);
                            getFrames(video, setup, top, impact)
                        }
                    }, 100);
                } else {
                    getFrames(video, setup, top, impact)
                }
            }
        },

        reportText: function (url, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, setup, impact, top) {
            if (url !== null) {
                // console.log('here')
                const pelvis_rotation = fig2.data[1].y;
                const pelvis_tilt = fig2.data[0].y
                const pelvis_bend = fig2.data[0].y;
                const thorax_rotation = fig4.data[0].y;
                const thorax_bend = fig4.data[1].y;
                const head_tilt = fig7.data[0].y;
                const head_rotation = fig8.data[0].y;
                const arm_rotation = fig11.data[0].y;
                const arm_ground = fig11.data[1].y;

                setup = Number(setup)
                impact = Number(impact)
                top = Number(top)

                // console.log(pelvis_tilt)

                const length = pelvis_rotation.length;

                const pelvis_rot_margins = document.getElementById('pelvis_rot_store').innerHTML.split(', ');
                const thorax_rot_margins = document.getElementById('thorax_rot_store').innerHTML.split(', ');
                const head_rot_margins = document.getElementById('head_rot_store').innerHTML.split(', ');
                const head_tilt_margins = document.getElementById('head_tilt_store').innerHTML.split(', ');
                const pelvis_tilt_margins = document.getElementById('pelvis_bend_store').innerHTML.split(', ');
                const thorax_bend_margins = document.getElementById('thorax_bend_store').innerHTML.split(', ');

                // console.log(head_tilt_margins)

                const pelvis_rot = pelvis_rotation[Math.floor(setup * length)];
                const thorax_rot = thorax_rotation[Math.floor(setup * length)];
                const head_rot = head_rotation[Math.floor(setup * length)];
                const head_t = head_tilt[Math.floor(setup * length)]
                const pelvis_t = pelvis_tilt[Math.floor(setup * length)]
                const thorax_b = thorax_bend[Math.floor(setup * length)]

                const pelvis_rot_top = pelvis_rotation[Math.floor(top * length)];
                const thorax_rot_top = thorax_rotation[Math.floor(top * length)];
                const head_rot_top = head_rotation[Math.floor(top * length)];
                const head_tilt_top = head_tilt[Math.floor(top * length)];
                const pelvis_tilt_top = pelvis_tilt[Math.floor(top * length)]
                const thorax_bend_top = thorax_bend[Math.floor(top * length)]

                const pelvis_rot_impact = pelvis_rotation[Math.floor(impact * length)];
                const thorax_rot_impact = thorax_rotation[Math.floor(impact * length)];
                const head_rot_impact = head_rotation[Math.floor(impact * length)];
                const head_tilt_impact = head_tilt[Math.floor(impact * length)]
                const pelvis_tilt_impact = pelvis_tilt[Math.floor(impact * length)]
                const thorax_bend_impact = thorax_bend[Math.floor(impact * length)]

                let pelvis_report_text = document.getElementById('pelvis_report_text');
                let thorax_report_text = document.getElementById('thorax_report_text');
                let head_report_text = document.getElementById('head_report_text');
                let head_report_text_tilt = document.getElementById('head_report_text_tilt')
                let pelvis_report_text_tilt = document.getElementById('pelvis_report_text_tilt')
                let thorax_report_text_bend = document.getElementById('thorax_report_text_bend')

                let pelvis_report_text_top = document.getElementById('pelvis_report_text_top');
                let thorax_report_text_top = document.getElementById('thorax_report_text_top');
                let head_report_text_top = document.getElementById('head_report_text_top');
                let head_report_text_tilt_top = document.getElementById('head_report_text_tilt_top')
                let pelvis_report_text_tilt_top = document.getElementById('pelvis_report_text_tilt_top')
                let thorax_report_text_bend_top = document.getElementById('thorax_report_text_bend_top')

                let pelvis_report_text_impact = document.getElementById('pelvis_report_text_impact');
                let thorax_report_text_impact = document.getElementById('thorax_report_text_impact');
                let head_report_text_impact = document.getElementById('head_report_text_impact');
                let head_report_text_tilt_impact = document.getElementById('head_report_text_tilt_impact')
                let pelvis_report_text_tilt_impact = document.getElementById('pelvis_report_text_tilt_impact')
                let thorax_report_text_bend_impact = document.getElementById('thorax_report_text_bend_impact')

                // Focus
                let focusReportText = document.getElementById('focus_report_text')
                let focusReportText2 = document.getElementById('focus_report_text_2')
                let focusReportTextTop = document.getElementById('focus_report_text_top')
                let focusReportTextTop2 = document.getElementById('focus_report_text_2_top')
                let focusReportTextImpact = document.getElementById('focus_report_text_impact')
                let focusReportTextImpact2 = document.getElementById('focus_report_text_2_impact')

                const errorPelvis = rotationText(pelvis_rot, pelvis_rot_margins, 'pelvis', pelvis_report_text)
                const errorThorax = rotationText(thorax_rot, thorax_rot_margins, 'thorax', thorax_report_text)
                const errorHead = rotationText(head_rot, head_rot_margins, 'head', head_report_text)
                const errorHeadTilt = tiltText(head_t, head_tilt_margins, 'head', head_report_text_tilt)
                const errorPelvisTilt = tiltText(pelvis_t, pelvis_tilt_margins, 'pelvis', pelvis_report_text_tilt)
                const errorThoraxBend = bendText(thorax_b, thorax_bend_margins, 'thorax', thorax_report_text_bend)
                const focusText = getFocus([errorPelvis, errorThorax, errorPelvisTilt, errorThoraxBend])

                focusReportText.innerHTML = focusText[0]
                focusReportText2.innerHTML = focusText[1]

                const errorPelvisTop = rotationText(pelvis_rot_top, pelvis_rot_margins.slice(2, 4), 'pelvis', pelvis_report_text_top)
                const errorThoraxTop = rotationText(thorax_rot_top, thorax_rot_margins.slice(2, 4), 'thorax', thorax_report_text_top)
                const errorHeadTop = rotationText(head_rot_top, head_rot_margins.slice(2, 4), 'head', head_report_text_top)
                const errorHeadTiltTop = tiltText(head_tilt_top, head_tilt_margins.slice(2, 4), 'head', head_report_text_tilt_top)
                const errorPelvisTiltTop = tiltText(pelvis_tilt_top, pelvis_tilt_margins.slice(2, 4), 'pelvis', pelvis_report_text_tilt_top)
                const errorThoraxBendTop = bendText(thorax_bend_top, thorax_bend_margins.slice(2, 4), 'thorax', thorax_report_text_bend_top)
                const focusTextTop = getFocus([errorPelvisTop, errorThoraxTop, errorPelvisTiltTop, errorThoraxBendTop])

                focusReportTextTop.innerHTML = focusTextTop[0]
                focusReportTextTop2.innerHTML = focusTextTop[1]

                const errorPelvisImpact = rotationTextDown(pelvis_rot_impact, pelvis_rot_margins.slice(4, 7), 'pelvis', pelvis_report_text_impact)
                const errorThoraxImpact = rotationTextDown(thorax_rot_impact, thorax_rot_margins.slice(4, 6), 'thorax', thorax_report_text_impact)
                const errorHeadImpact = rotationTextDown(head_rot_impact, head_rot_margins.slice(4, 6), 'head', head_report_text_impact)
                const errorHeadTiltImpact = tiltText(head_tilt_impact, head_tilt_margins.slice(4, 7), 'head', head_report_text_tilt_impact)
                const errorPelvisTiltImpact = tiltText(pelvis_tilt_impact, pelvis_tilt_margins.slice(4, 7), 'pelvis', pelvis_report_text_tilt_impact)
                const errorThoraxBendImpact = bendText(thorax_bend_impact, thorax_bend_margins.slice(4, 7), 'thorax', thorax_report_text_bend_impact)
                const focusTextImpact = getFocus([errorPelvisImpact, errorThoraxImpact, errorPelvisTiltImpact, errorThoraxBendImpact])

                focusReportTextImpact.innerHTML = focusTextImpact[0]
                focusReportTextImpact2.innerHTML = focusTextImpact[1]

            }
        },


        uploadComponent: function (children) {
            var uploadDataInitial = document.getElementById('upload-initial').children[0].children[1]
            if (uploadDataInitial.childElementCount > 0) {
                console.log(uploadDataInitial);
                uploadDataInitial.children[0].classList.add('h-full');
                console.log(uploadDataInitial);
            } else {
                // wait for the element to be created
                setInterval(function () {
                        if (uploadDataInitial.childElementCount > 0) {
                            uploadDataInitial.children[0].classList.add('h-full');
                        }
                    }
                )
            }
        },

        changeBallflightBtnBorder: function (high_time, low_time, mid_time, left_time, right_time, straight_time, topped_time, fat_time, socket_time, airshot_time, center_time) {
            var highBtn = document.getElementById('high_btn').classList
            var lowBtn = document.getElementById('low_btn').classList
            var midBtn = document.getElementById('mid_btn').classList
            var leftBtn = document.getElementById('left_btn').classList
            var rightBtn = document.getElementById('right_btn').classList
            var straightBtn = document.getElementById('straight_btn').classList
            var toppedBtn = document.getElementById('topped_btn').classList
            var fatBtn = document.getElementById('fat_btn').classList
            var socketBtn = document.getElementById('socket_btn').classList
            var airshotBtn = document.getElementById('air_shot_btn').classList
            var centerBtn = document.getElementById('center_btn').classList

            highBtn.remove('border-slate-900')
            lowBtn.remove('border-slate-900')
            midBtn.remove('border-slate-900')
            leftBtn.remove('border-slate-900')
            rightBtn.remove('border-slate-900')
            straightBtn.remove('border-slate-900')
            toppedBtn.remove('border-slate-900')
            fatBtn.remove('border-slate-900')
            socketBtn.remove('border-slate-900')
            airshotBtn.remove('border-slate-900')
            centerBtn.remove('border-slate-900')

            highBtn.remove('dark:border-gray-100')
            lowBtn.remove('dark:border-gray-100')
            midBtn.remove('dark:border-gray-100')
            leftBtn.remove('dark:border-gray-100')
            rightBtn.remove('dark:border-gray-100')
            straightBtn.remove('dark:border-gray-100')
            toppedBtn.remove('dark:border-gray-100')
            fatBtn.remove('dark:border-gray-100')
            socketBtn.remove('dark:border-gray-100')
            airshotBtn.remove('dark:border-gray-100')
            centerBtn.remove('dark:border-gray-100')


            // check height (get highest timestamp)
            const height_dict = {highBtn: high_time, lowBtn: low_time, midBtn: mid_time};
            // replace null with 0
            Object.keys(height_dict).forEach(key => {
                if (height_dict[key] === undefined) {
                    height_dict[key] = 0;
                }
            });
            const height = Object.keys(height_dict).reduce((a, b) => height_dict[a] > height_dict[b] ? a : b);

            switch (height) {
                case 'highBtn':
                    if (high_time > 0) {
                        highBtn.add('border-slate-900');
                        highBtn.add('dark:border-gray-100')
                    }
                    break;
                case 'lowBtn':
                    if (low_time > 0) {
                        lowBtn.add('border-slate-900');
                        lowBtn.add('dark:border-gray-100')
                    }
                    break;
                case 'midBtn':
                    if (mid_time > 0) {
                        midBtn.add('border-slate-900');
                        midBtn.add('dark:border-gray-100')
                    }
                    break;
                default:
                    // Handle unexpected value of height
                    break;
            }

            // check direction
            const direction_dict = {leftBtn: left_time, rightBtn: right_time, straightBtn: straight_time};
            // replace null with 0
            Object.keys(direction_dict).forEach(key => {
                if (direction_dict[key] === undefined) {
                    direction_dict[key] = 0;
                }
            });
            const direction = Object.keys(direction_dict).reduce((a, b) => direction_dict[a] > direction_dict[b] ? a : b);

            switch (direction) {
                case 'leftBtn':
                    if (left_time > 0) {
                        leftBtn.add('border-slate-900');
                        leftBtn.add('dark:border-gray-100')
                    }
                    break;
                case 'rightBtn':
                    if (right_time > 0) {
                        rightBtn.add('border-slate-900');
                        rightBtn.add('dark:border-gray-100')
                    }
                    break;
                case 'straightBtn':
                    if (straight_time > 0) {
                        straightBtn.add('border-slate-900');
                        straightBtn.add('dark:border-gray-100')
                    }
                    break;
                default:
                    // Handle unexpected value of direction
                    break;
            }

            // check contact
            const contact_dict = {
                toppedBtn: topped_time,
                fatBtn: fat_time,
                socketBtn: socket_time,
                airshotBtn: airshot_time,
                centerBtn: center_time
            };
            // replace null with 0
            Object.keys(contact_dict).forEach(key => {
                if (contact_dict[key] === undefined) {
                    contact_dict[key] = 0;
                }
            });
            const contact = Object.keys(contact_dict).reduce((a, b) => contact_dict[a] > contact_dict[b] ? a : b);

            switch (contact) {
                case 'toppedBtn':
                    if (topped_time > 0) {
                        toppedBtn.add('border-slate-900');
                        toppedBtn.add('dark:border-gray-100')
                    }
                    break;
                case 'fatBtn':
                    if (fat_time > 0) {
                        fatBtn.add('border-slate-900');
                        fatBtn.add('dark:border-gray-100')
                    }
                    break;
                case 'socketBtn':
                    if (socket_time > 0) {
                        socketBtn.add('border-slate-900');
                        socketBtn.add('dark:border-gray-100')
                    }
                    break;
                case 'airshotBtn':
                    if (airshot_time > 0) {
                        airshotBtn.add('border-slate-900');
                        airshotBtn.add('dark:border-gray-100')
                    }
                    break;
                case 'centerBtn':
                    if (center_time > 0) {
                        centerBtn.add('border-slate-900');
                        centerBtn.add('dark:border-gray-100')
                    }
                    break;
                default:
                    // Handle unexpected value of contact
                    break;
            }

        }

    },

});


// Helper functions


function getFocus(errorArray) {
    //     sort the array
    errorArray.sort((a, b) => b[0] - a[0]);
    //     get the first two elements
    return [errorArray[0][1], errorArray[1][1]];
}


// Define the takeSnapshot function
function takeSnapshot(video, canvas, time) {
    return new Promise(function (resolve, reject) {
        const ctx = canvas.getContext("2d");

        // Set the width and height of the canvas
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Create a closure to capture the current time value
        function captureSnapshot() {
            setTimeout(function () {
                // Draw the frame onto the canvas
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                // Remove the event listener
                video.removeEventListener("seeked", captureSnapshot);

                // Resolve the promise
                resolve();
            }, 5);
        }

        // Seek to the desired time
        video.currentTime = time;

        // Wait for the video to load that specific frame
        video.addEventListener("seeked", captureSnapshot, false);
    });
}

function rotationText(angle, margin, body_part, element) {
    if (angle < margin[0]) {
        const text = `Rotate your ${body_part} a little less to the right.`
        element.innerHTML = text
        return [Math.abs(margin[0] - angle) / Math.abs(margin[0] - margin[1]), text]
    } else if (angle > margin[1]) {
        const text = `Rotate your ${body_part} a little more to the right.`
        element.innerHTML = text
        return [Math.abs(margin[1] - angle) / Math.abs(margin[0] - margin[1]), text]
    } else {
        body_part = body_part.charAt(0).toUpperCase() + body_part.slice(1)
        const text = `${body_part} rotation: 👍`
        element.innerHTML = text
        return [0, text]
    }
}

function rotationTextDown(angle, margin, body_part, element) {
    if (angle < margin[0]) {
        const text = `Rotate your ${body_part} a little more to the left.`
        element.innerHTML = text
        return [Math.abs(margin[0] - angle) / Math.abs(margin[0] - margin[1]), text]
    } else if (angle > margin[1]) {
        const text = `Rotate your ${body_part} a little less to the left.`
        element.innerHTML = text
        return [Math.abs(margin[1] - angle) / Math.abs(margin[0] - margin[1]), text]
    } else {
        body_part = body_part.charAt(0).toUpperCase() + body_part.slice(1)
        const text = `${body_part} rotation: 👍`
        element.innerHTML = text
        return [0, text]
    }
}

function tiltText(angle, margin, body_part, element) {
    if (angle < margin[0]) {
        const text = `Tilt your ${body_part} a little less to the right.`
        element.innerHTML = text
        return [Math.abs(margin[0] - angle) / Math.abs(margin[0] - margin[1]), text]
    } else if (angle > margin[1]) {
        const text = `Tilt your ${body_part} a little more to the right.`
        element.innerHTML = text
        return [Math.abs(margin[1] - angle) / Math.abs(margin[0] - margin[1]), text]
    } else {
        body_part = body_part.charAt(0).toUpperCase() + body_part.slice(1)
        const text = `${body_part} tilt: 👍`
        element.innerHTML = text
        return [0, text]
    }
}


function bendText(angle, margin, body_part, element) {
    if (angle < margin[0]) {
        const text = `Bend your ${body_part} a little more forward.`
        element.innerHTML = text
        return [Math.abs(margin[0] - angle) / Math.abs(margin[0] - margin[1]), text]
    } else if (angle > margin[1]) {
        const text = `Bend your ${body_part} a little less forward.`
        element.innerHTML = text
        return [Math.abs(margin[1] - angle) / Math.abs(margin[0] - margin[1]), text]
    } else {
        body_part = body_part.charAt(0).toUpperCase() + body_part.slice(1)
        const text = `${body_part} bend: 👍`
        element.innerHTML = text
        return [0, text]
    }
}


function newGradient(low, high, marginLow, marginHigh, slackYellow = 5, slackRed = 10) {
    const positionLow = (low + Number(marginLow)) / (high + low) * 100
    const positionHigh = (low + Number(marginHigh)) / (high + low) * 100
    const positionYL = positionLow - slackYellow
    const positionYH = positionHigh + slackYellow
    const positionRL = positionLow - slackRed
    const positionRH = positionHigh + slackRed

    // console.log(low, high, marginLow, marginHigh, slackYellow, slackRed)
    // console.log(positionLow, positionHigh, positionYL, positionYH, positionRL, positionRH)

    // `linear-gradient(to right, #f43f5e, 10%, #fde047 ${pelvisRotLow},#84cc16 ${pelvisRotLow} ${pelvisRotHigh}, #fde047 60%, 80%, #f43f5e)`
    // console.log(`linear-gradient(to right, #f43f5e, ${positionRL}, #fde047 ${positionYL}%,#84cc16 ${positionLow}% ${positionHigh}%, #fde047 ${positionYH}%, ${positionRH}%, #f43f5e)`)

    return `linear-gradient(to right, #f43f5e, ${positionRL}%, #fde047 ${positionYL}%,#84cc16 ${positionLow}% ${positionHigh}%, #fde047 ${positionYH}%, ${positionRH}%, #f43f5e)`
}

function resetGradient() {
    return `linear-gradient(#84cc16 0% 100%)`
}

function getColorFromGradient(gradient, low, high, value) {
    const computedStyle = getComputedStyle(gradient);
    const regex = /rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)/g;
    const rgbColors = computedStyle.backgroundImage.match(regex);
    const colorPercents = computedStyle.backgroundImage.match(/(\d+(?:\.\d+)?)%/g)
    const positionPercent = (value - low) / (high - low)

    // Get closest colors by percentage
    let colorIndex = colorPercents.length - 1
    for (let i = colorPercents.length - 1; i >= 0; i--) {
        if (positionPercent * 100 > colorPercents[i].replace('%', '')) {
            break
        }
        colorIndex = i
    }

    const percentLimitUp = colorPercents[colorIndex].replace('%', '') / 100
    let percentLimitDown = colorPercents[0].replace('%', '') / 100
    if (colorIndex !== 0) {
        percentLimitDown = colorPercents[colorIndex - 1].replace('%', '') / 100
    }

    // console.log(percentLimitUp, percentLimitDown)

    const maxColorIndex = colorIndex
    let minColorIndex = 0
    if (colorIndex !== 0) {
        minColorIndex = colorIndex - 1
    }

    const maxColor = rgbColors[maxColorIndex]
    const minColor = rgbColors[minColorIndex]

    let percent = (positionPercent - (percentLimitDown)) / (percentLimitUp - percentLimitDown)

    if (percent < 0) {
        percent = 0
    }
    if (percent > 1) {
        percent = 1
    }

    // console.log(percent)
    // console.log(positionPercent)

    function blendColors(color1, color2, percent) {
        // console.log(color1, color2, percent)
        const [r1, g1, b1] = color1.match(/\d+/g).map(Number);
        const [r2, g2, b2] = color2.match(/\d+/g).map(Number);
        const r = Math.round(r1 + (r2 - r1) * percent);
        const g = Math.round(g1 + (g2 - g1) * percent);
        const b = Math.round(b1 + (b2 - b1) * percent);
        return `rgb(${r}, ${g}, ${b})`;
    }

    return blendColors(minColor, maxColor, percent)

}

function getFrames(video, setup, top, impact) {

    var canvas = document.getElementById("setup_frame");

    var canvas_impact = document.getElementById("impact_frame");

    var canvas_top = document.getElementById("top_frame");

    // wait for the video to load
    video.onloadeddata = function () {
        const duration = video.duration;

        const previousTime = video.currentTime;

        // Take the first snapshot
        takeSnapshot(video, canvas, setup * duration).then(function () {
            // Wait for the first snapshot to finish loading before taking the second one
            return takeSnapshot(video, canvas_top, top * duration);
        }).then(function () {
            // Wait for the second snapshot to finish loading before taking the third one
            return takeSnapshot(video, canvas_impact, impact * duration);
        }).then(function () {
            // Wait for the third snapshot to finish loading before resetting the video
            video.currentTime = previousTime;
            // All snapshots have finished loading
            // console.log("All snapshots taken");
        }).catch(function (error) {
            // Handle any errors that may occur
            console.error(error);
        });

    }
}
