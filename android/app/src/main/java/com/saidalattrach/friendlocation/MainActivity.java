package com.saidalattrach.friendlocation;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.IBinder;
import android.support.v7.widget.SwitchCompat;
import android.view.MotionEvent;
import android.view.View;
import android.widget.CompoundButton;
import android.widget.NumberPicker;
import android.widget.TextView;

import com.google.android.gms.common.api.Status;

import org.w3c.dom.Text;

public class MainActivity extends Activity
{
    private static final int SETTINGS_REQUEST_CODE = 1;

    private static final int MIN_UPDATE_INTERVAL = 1;
    private static final int MAX_UPDATE_INTERVAL = 120;
    private static final int DEFAULT_UPDATE_INTERVAL = 30;

    private boolean isServiceBound = false;

    private MainService service;
    private Intent serviceIntent;
    private ServiceConnection serviceConnection;
    private SwitchCompat enableToggle;

    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);

        serviceIntent = new Intent(this, MainService.class);

        serviceConnection = new ServiceConnection() {
            public void onServiceConnected(ComponentName name, IBinder binder)
            {
                isServiceBound = true;
                service = ((MainService.LocalBinder) binder).getService();
                service.requesLocationUpdates((Status status) ->
                {
                    if (status.hasResolution())
                    {
                        try
                        {
                            status.startResolutionForResult(MainActivity.this, SETTINGS_REQUEST_CODE);
                        } catch (Exception ignored) {}
                    }
                });
            }

            public void onServiceDisconnected(ComponentName name)
            {
                isServiceBound = false;
                service = null;
            }
        };

        setContentView(R.layout.activity_main);

        enableToggle = (SwitchCompat) findViewById(R.id.enable_update);
        enableToggle.setOnCheckedChangeListener((CompoundButton buttonView, boolean isChecked) ->
        {
            if (isChecked)
                startMainService();
            else
                stopMainService();
        });

        NumberPicker picker = (NumberPicker) findViewById(R.id.update_interval_picker);
        picker.setMinValue(MIN_UPDATE_INTERVAL);
        picker.setMaxValue(MAX_UPDATE_INTERVAL);
        picker.setValue(DEFAULT_UPDATE_INTERVAL);
        picker.setOnValueChangedListener((NumberPicker p, int oldVal, int newVal) ->
        {
            newVal *= 60 * 1000;
            setUpdateInterval(newVal);
        });

        TextView textView = (TextView) findViewById(R.id.test_text);
        textView.setOnTouchListener((View v, MotionEvent event) ->
        {
            if (service != null)
            {
                int a = 0;
            }
            return true;
        });
    }

    protected void onStart()
    {
        super.onStart();
        if (enableToggle.isChecked())
            startMainService();
        else
            stopMainService();
    }

    protected void onStop()
    {
        super.onStop();
        if (service != null)
            unbindService(serviceConnection);
    }

    private void startMainService()
    {
        startService(serviceIntent);
        bindService(serviceIntent, serviceConnection, 0);
        if (isServiceBound)
            unbindService(serviceConnection);
    }

    private void stopMainService()
    {
        if (isServiceBound)
        {
            unbindService(serviceConnection);
            stopService(serviceIntent);
        }
    }

    private void setUpdateInterval(long interval)
    {
        if (service != null)
            service.setUpdateInterval(interval);
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data)
    {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == SETTINGS_REQUEST_CODE)
        {
            if (resultCode == RESULT_OK)
                service.requesLocationUpdates((Status status) ->
                {
                    if (!status.isSuccess())
                        enableToggle.setChecked(false);
                });
            else
                enableToggle.setChecked(false);
        }
    }
}
