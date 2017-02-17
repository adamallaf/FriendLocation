package com.saidalattrach.friendlocation;

import android.app.Activity;

import android.content.ComponentName;
import android.content.Intent;
import android.content.IntentSender;
import android.content.ServiceConnection;

import android.os.Bundle;
import android.os.IBinder;

import android.view.KeyEvent;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.NumberPicker;

import android.support.v7.widget.SwitchCompat;
import android.widget.TextView;

import com.google.android.gms.common.api.Status;

public class MainActivity extends Activity
{
    private static final int SETTINGS_REQUEST_CODE = 1;

    private static final int MIN_UPDATE_INTERVAL = 1;
    private static final int MAX_UPDATE_INTERVAL = 120;
    private static final int DEFAULT_UPDATE_INTERVAL = 30;

    private int updateInterval = DEFAULT_UPDATE_INTERVAL;

    private boolean isServiceBound = false;
    private Intent serviceIntent;
    private ServiceConnection serviceConnection;
    private SwitchCompat enableToggle;
    private MainService.LocalBinder localBinder;

    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);

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
            updateInterval = newVal;
            newVal *= 60 * 1000;
            setUpdateInterval(newVal);
        });

        EditText ipAddress = (EditText) findViewById(R.id.ip_address);
        ipAddress.setOnEditorActionListener((TextView v, int actionId, KeyEvent event) ->
                {
                    TheServed.setHost(v.getText().toString());
                    return true;
                }
        );

        EditText username = (EditText) findViewById(R.id.username);
        username.setOnEditorActionListener((TextView v, int actionId, KeyEvent event) ->
                {
                    if (localBinder != null)
                        localBinder.setUsername(v.getText().toString());
                    return true;
                }
        );

        serviceIntent = new Intent(this, MainService.class);

        serviceConnection = new ServiceConnection()
        {
            public void onServiceConnected(ComponentName name, IBinder binder)
            {
                isServiceBound = true;
                localBinder = (MainService.LocalBinder) binder;
                localBinder.getStatus((Status status) ->
                {
                    if (!status.isSuccess() && status.hasResolution())
                    {
                        try
                        {
                            status.startResolutionForResult(MainActivity.this, SETTINGS_REQUEST_CODE);
                        } catch (IntentSender.SendIntentException ignored) {}
                    }
                    else
                    {
                        localBinder.setUsername(username.getText().toString());
                        TheServed.setHost(ipAddress.getText().toString());
                    }
                });
            }

            public void onServiceDisconnected(ComponentName name)
            {
                isServiceBound = false;
            }
        };
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
        unbindMainService();
    }

    private void startMainService()
    {
        serviceIntent.putExtra("UPDATE_INTERVAL", updateInterval);
        startService(serviceIntent);
        bindService(serviceIntent, serviceConnection, 0);
    }

    private void stopMainService()
    {
        if (isServiceBound)
        {
            unbindService(serviceConnection);
            isServiceBound = false;
        }
        stopService(serviceIntent);
    }

    private void unbindMainService()
    {
        if (isServiceBound)
        {
            unbindService(serviceConnection);
            isServiceBound = false;
        }
    }

    private void setUpdateInterval(long interval)
    {
        if (localBinder != null)
            localBinder.setUpdateInterval(interval);
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data)
    {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == SETTINGS_REQUEST_CODE)
        {
            if (resultCode == RESULT_OK)
                startMainService();
            else
                enableToggle.setChecked(false);
        }
    }
}
