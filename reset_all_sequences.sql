-- Reset ID sequences for all tables in MyMurid database
-- This script sets each sequence to continue from the current maximum ID + 1
-- If a table is empty, it will start from 1

-- Function to safely reset a sequence
DO $$
DECLARE
    max_id INTEGER;
BEGIN
    -- student_info
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM student_info;
    PERFORM setval('student_info_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset student_info_id_seq to %', GREATEST(max_id, 1);

    -- menu_item
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM menu_item;
    PERFORM setval('menu_item_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset menu_item_id_seq to %', GREATEST(max_id, 1);

    -- order
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM "order";
    PERFORM setval('order_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset order_id_seq to %', GREATEST(max_id, 1);

    -- feedback
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM feedback;
    PERFORM setval('feedback_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset feedback_id_seq to %', GREATEST(max_id, 1);

    -- feedback_media
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM feedback_media;
    PERFORM setval('feedback_media_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset feedback_media_id_seq to %', GREATEST(max_id, 1);

    -- vote
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM vote;
    PERFORM setval('vote_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset vote_id_seq to %', GREATEST(max_id, 1);

    -- top_up
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM top_up;
    PERFORM setval('top_up_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset top_up_id_seq to %', GREATEST(max_id, 1);

    -- parent
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM parent;
    PERFORM setval('parent_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset parent_id_seq to %', GREATEST(max_id, 1);

    -- parent_child
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM parent_child;
    PERFORM setval('parent_child_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset parent_child_id_seq to %', GREATEST(max_id, 1);

    -- payment
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM payment;
    PERFORM setval('payment_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset payment_id_seq to %', GREATEST(max_id, 1);

    -- reward_category
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM reward_category;
    PERFORM setval('reward_category_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset reward_category_id_seq to %', GREATEST(max_id, 1);

    -- achievement
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM achievement;
    PERFORM setval('achievement_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset achievement_id_seq to %', GREATEST(max_id, 1);

    -- student_points
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM student_points;
    PERFORM setval('student_points_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset student_points_id_seq to %', GREATEST(max_id, 1);

    -- reward_item
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM reward_item;
    PERFORM setval('reward_item_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset reward_item_id_seq to %', GREATEST(max_id, 1);

    -- student_redemption
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM student_redemption;
    PERFORM setval('student_redemption_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset student_redemption_id_seq to %', GREATEST(max_id, 1);

    -- directory
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM directory;
    -- Create sequence if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_sequences WHERE schemaname = 'public' AND sequencename = 'directory_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE directory_id_seq OWNED BY directory.id');
        -- Set the column default to use the sequence
        EXECUTE format('ALTER TABLE directory ALTER COLUMN id SET DEFAULT nextval(''directory_id_seq'')');
        RAISE NOTICE 'Created directory_id_seq sequence and linked to directory.id';
    END IF;
    PERFORM setval('directory_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset directory_id_seq to %', GREATEST(max_id, 1);

    -- facility
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM facility;
    PERFORM setval('facility_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset facility_id_seq to %', GREATEST(max_id, 1);

    -- transaction
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM transaction;
    PERFORM setval('transaction_id_seq', GREATEST(max_id, 1), false);
    RAISE NOTICE 'Reset transaction_id_seq to %', GREATEST(max_id, 1);

    RAISE NOTICE 'All sequences have been reset successfully!';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error resetting sequences: %', SQLERRM;
END $$;

